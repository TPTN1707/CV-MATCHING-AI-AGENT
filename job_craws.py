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

# URL tìm kiếm cơ sở (không bao gồm tham số trang)
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
    """Xây dựng URL cho từng trang kết quả tìm kiếm."""
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}page={page_number}"



def _extract_links_from_html(html_content: str) -> set[str]:
    """Phân tích HTML và trích xuất các liên kết tuyển dụng hợp lệ."""
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
    Trích xuất chỉ phần nội dung job posting từ HTML đã parse.
    Lấy các section: Job title, Minimum/Preferred qualifications, About the job, Responsibilities.
    Bỏ qua navigation, footer, EEO policy, social links...
    """
    content_parts: list[str] = []

    # Lấy tiêu đề job (thường nằm trong h2 đầu tiên sau "Job Details")
    job_title_tag = parsed.find("h2")
    if job_title_tag:
        content_parts.append(job_title_tag.get_text(strip=True))

    # Các section chứa nội dung job thực sự
    target_sections = [
        "Minimum qualifications",
        "Preferred qualifications",
        "About the job",
        "Responsibilities",
    ]

    for heading in parsed.find_all("h3"):
        heading_text = heading.get_text(strip=True).rstrip(":")
        if heading_text in target_sections:
            # Lấy tất cả nội dung giữa heading này và heading tiếp theo
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
    Thu thập liên kết việc làm từ nhiều trang kết quả tìm kiếm.
    """
    all_links: set[str] = set()

    with httpx.Client(headers=_REQUEST_HEADERS, follow_redirects=True, timeout=15.0) as client:
        for page_idx in range(1, pages + 1):
            target_url = _build_page_url(base_url, page_idx)
            logger.info("Đang tải trang %d: %s", page_idx, target_url)

            try:
                resp = client.get(target_url)
                resp.raise_for_status()
            except httpx.HTTPStatusError as err:
                logger.warning("Lỗi HTTP %d ở trang %d – bỏ qua", err.response.status_code, page_idx)
                continue
            except httpx.RequestError as err:
                logger.error("Lỗi mạng ở trang %d: %s", page_idx, err)
                continue

            page_links = _extract_links_from_html(resp.text)
            all_links.update(page_links)
            logger.info("Trang %d thu được %d liên kết (tổng: %d)", page_idx, len(page_links), len(all_links))

    logger.info("Hoàn tất crawl – thu được %d URL việc làm từ %d trang", len(all_links), pages)
    return sorted(all_links)



async def _fetch_page_content(client: httpx.AsyncClient, url: str) -> Optional[Document]:
    """Tải nội dung một trang job posting và trích xuất phần mô tả công việc."""
    try:
        resp = await client.get(url)
        resp.raise_for_status()
    except (httpx.HTTPStatusError, httpx.RequestError) as err:
        logger.warning("Không thể tải %s: %s", url, err)
        return None

    parsed = BeautifulSoup(resp.text, "html.parser")

    # Loại bỏ script/style trước khi xử lý
    for tag in parsed(["script", "style"]):
        tag.decompose()

    # Trích xuất chỉ nội dung job, không lấy toàn bộ trang
    job_content = _extract_job_content(parsed)

    if not job_content.strip():
        # Fallback: nếu không parse được theo cấu trúc, lấy text thô nhưng loại bỏ nav/footer
        for tag in parsed(["nav", "footer", "header"]):
            tag.decompose()
        job_content = parsed.get_text(separator="\n", strip=True)

    if not job_content.strip():
        return None

    # Lấy title từ thẻ <title> hoặc từ h2 đầu tiên
    title_tag = parsed.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""

    return Document(
        page_content=job_content,
        metadata={"source": url, "title": title_text},
    )



async def _scrape_all_urls(urls: list[str], concurrency: int = 8) -> list[Document]:
    """Tải song song nhiều URL với giới hạn số lượng kết nối đồng thời."""
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
            logger.warning("Lỗi không mong đợi khi scrape: %s", result)

    return documents

async def ingest_jobs():
    """Thu thập mô tả công việc từ web và lưu vào ChromaDB."""
    logger.info("Bắt đầu quy trình thu thập dữ liệu việc làm...")

    # Bước 1: Thu thập danh sách URL việc làm
    job_urls = get_job_urls(BASE_SEARCH_URL, pages=5)

    if not job_urls:
        logger.warning("Không tìm thấy URL việc làm nào – dừng thu thập.")
        return

    logger.info("Đang tải nội dung từ %d URL đã thu thập...", len(job_urls))
    print(job_urls)

    # Bước 2: Tải nội dung các trang song song
    documents = await _scrape_all_urls(job_urls)

    if not documents:
        logger.warning("Không tải được tài liệu nào từ các URL.")
        return

    logger.info("Đã tải thành công %d tài liệu", len(documents))

    # Bước 3: Xóa collection cũ (nếu tồn tại) để tránh dữ liệu trùng lặp
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    existing_collections = [c.name for c in chroma_client.list_collections()]
    if "job_postings" in existing_collections:
        chroma_client.delete_collection("job_postings")
        logger.info("Đã xóa collection cũ 'job_postings'")

    # Bước 4: Tạo embeddings và lưu vào vector store mới
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
        logger.info("Đang lập chỉ mục lô %d/%d (%d tài liệu)...", chunk_idx + 1, total_chunks, len(chunk))
        try:
            await vector_store.aadd_documents(chunk)
        except Exception as exc:
            logger.error("Lỗi khi lập chỉ mục lô %d: %s", chunk_idx + 1, exc)

    total_indexed = vector_store._collection.count()
    logger.info("Hoàn tất thu thập – %d tài liệu đã được lưu trong vector store.", total_indexed)


if __name__ == "__main__":
    asyncio.run(ingest_jobs())