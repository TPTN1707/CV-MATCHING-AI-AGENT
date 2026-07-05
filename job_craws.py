import asyncio
import logging
from typing import Optional
from urllib.parse import urljoin
from webbrowser import Chrome

import chromadb
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Base search URL (without the page query parameter)
BASE_SEARCH_URL = "https://www.google.com/about/careers/applications/jobs/results?location=Vietnam"
_CAREERS_ORIGIN = "https://www.google.com/about/careers/applications/"

_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ),
}


def _build_page_url(base_url: str, page_number: int) -> str:
    """Build the URL for a specific search results page."""
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}page={page_number}"


def _extract_links_from_html(html_content: str) -> set[str]:
    """Parse HTML and extract valid job posting links."""
    parsed = BeautifulSoup(html_content, "html.parser")
    collected = set()
    anchor_elements = parsed.select("a[href*='jobs/results/']")
    for anchor in anchor_elements:
        raw_href = anchor.get("href", "")
        if raw_href:
            absolute = urljoin(_CAREERS_ORIGIN, raw_href)
            collected.add(absolute)
    return collected


def _extract_job_content(parsed: BeautifulSoup) -> str:
    """
    Extract only the job posting content from the parsed HTML.
    Include the following sections:
    Job title, Minimum/Preferred qualifications,
    About the job, Responsibilities.
    Exclude navigation, footer, EEO policy, social links, etc.
    """
    content_parts: list[str] = []

    # Extract the job title (usually the first h2 after "Job Details")
    job_title_tag = parsed.find("h2")
    if job_title_tag:
        content_parts.append(job_title_tag.get_text(strip=True))

    # Sections containing the actual job description
    target_sections = [
        "Minimum qualifications",
        "Preferred qualifications",
        "About the job",
        "Responsibilities",
    ]

    for heading in parsed.find_all("h3"):
        heading_text = heading.get_text(strip=True).rstrip(":")
        if heading_text in target_sections:
            # Extract all content between this heading and the next heading
            section_content = []
            sibling = heading.find_next_sibling()
            while sibling and sibling.name not in ("h2", "h3"):
                text = sibling.get_text(separator="\n", strip=True)
                if text:
                    section_content.append(text)
                sibling = sibling.find_next_sibling()
            if section_content:
                content_parts.append(f"\n{heading_text}:\n" + "\n".join(section_content))

    return "\n\n".join(content_parts)


def get_job_urls(base_url: str, pages: int = 5) -> list[str]:
    """
    Collect job posting links from multiple search result pages.
    """
    all_links: set[str] = set()

    with httpx.Client(headers=_REQUEST_HEADERS, follow_redirects=True, timeout=15.0) as client:
        for page_idx in range(1, pages + 1):
            target_url = _build_page_url(base_url, page_idx)
            logger.info("Loading page %d: %s", page_idx, target_url)

            try:
                resp = client.get(target_url)
                resp.raise_for_status()
            except httpx.HTTPStatusError as err:
                logger.warning("HTTP error %d on page %d – skipping", err.response.status_code, page_idx)
                continue
            except httpx.RequestError as err:
                logger.error("Network error on page %d: %s", page_idx, err)
                continue

            page_links = _extract_links_from_html(resp.text)
            all_links.update(page_links)
            logger.info(
                "Page %d collected %d links (total: %d)",
                page_idx,
                len(page_links),
                len(all_links),
            )

    logger.info(
        "Crawling completed – collected %d job URLs from %d pages",
        len(all_links),
        pages,
    )
    return sorted(all_links)


async def _fetch_page_content(client: httpx.AsyncClient, url: str) -> Optional[Document]:
    """Fetch a job posting page and extract the job description."""
    try:
        resp = await client.get(url)
        resp.raise_for_status()
    except (httpx.HTTPStatusError, httpx.RequestError) as err:
        logger.warning("Failed to fetch %s: %s", url, err)
        return None

    parsed = BeautifulSoup(resp.text, "html.parser")

    # Remove script/style tags before processing
    for tag in parsed(["script", "style"]):
        tag.decompose()

    # Extract only the job description instead of the entire page
    job_content = _extract_job_content(parsed)

    if not job_content.strip():
        # Fallback: if structured parsing fails, extract plain text while removing nav/footer/header
        for tag in parsed(["nav", "footer", "header"]):
            tag.decompose()
        job_content = parsed.get_text(separator="\n", strip=True)

    if not job_content.strip():
        return None

    # Get the title from the <title> tag or the first h2
    title_tag = parsed.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""

    return Document(
        page_content=job_content,
        metadata={"source": url, "title": title_text},
    )


async def _scrape_all_urls(urls: list[str], concurrency: int = 8) -> list[Document]:
    """Fetch multiple URLs concurrently with a limit on simultaneous connections."""
    semaphore = asyncio.Semaphore(concurrency)
    documents: list[Document] = []

    async def _bounded_fetch(url: str) -> Optional[Document]:
        async with semaphore:
            return await _fetch_page_content(client, url)

    async with httpx.AsyncClient(headers=_REQUEST_HEADERS, follow_redirects=True, timeout=20.0) as client:
        tasks = [_bounded_fetch(u) for u in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Document):
            documents.append(result)
        elif isinstance(result, Exception):
            logger.warning("Unexpected error while scraping: %s", result)

    return documents


async def ingest_jobs():
    """Collect job descriptions from the web and store them in ChromaDB."""
    logger.info("Starting the job data collection process...")

    # Step 1: Collect job posting URLs
    job_urls = get_job_urls(BASE_SEARCH_URL, pages=5)

    if not job_urls:
        logger.warning("No job URLs found – stopping ingestion.")
        return

    logger.info("Fetching content from %d collected URLs...", len(job_urls))
    print(job_urls)

    # Step 2: Fetch page contents concurrently
    documents = await _scrape_all_urls(job_urls)

    if not documents:
        logger.warning("No documents could be retrieved from the URLs.")
        return

    logger.info("Successfully fetched %d documents", len(documents))

    # Step 3: Delete the existing collection (if any) to avoid duplicate data
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    existing_collections = [c.name for c in chroma_client.list_collections()]
    if "job_postings" in existing_collections:
        chroma_client.delete_collection("job_postings")
        logger.info("Deleted existing collection 'job_postings'")

    # Step 4: Generate embeddings and store them in a new vector store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    vector_store = Chroma(
        collection_name="job_postings",
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )

    chunk_size = 15
    total_chunks = (len(documents) + chunk_size - 1) // chunk_size

    for chunk_idx in range(total_chunks):
        start = chunk_idx * chunk_size
        end = start + chunk_size
        chunk = documents[start:end]
        logger.info(
            "Indexing batch %d/%d (%d documents)...",
            chunk_idx + 1,
            total_chunks,
            len(chunk),
        )
        try:
            await vector_store.aadd_documents(chunk)
        except Exception as exc:
            logger.error("Failed to index batch %d: %s", chunk_idx + 1, exc)

    total_indexed = vector_store._collection.count()
    logger.info(
        "Ingestion completed – %d documents have been stored in the vector store.",
        total_indexed,
    )


if __name__ == "__main__":
    asyncio.run(ingest_jobs())