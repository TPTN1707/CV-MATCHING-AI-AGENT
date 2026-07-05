"""Defines the tools used by the job search agent."""

import asyncio
import logging
from typing import List, Dict, Union, Optional

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

logger = logging.getLogger(__name__)

# Shared vector store configuration
_COLLECTION_NAME = "job_postings"
_EMBEDDING_MODEL = "models/gemini-embedding-2"
_PERSIST_DIR = "./chroma_db"


def _get_vector_store() -> Chroma:
    """Initialize a connection to the ChromaDB vector store."""
    embedding_fn = GoogleGenerativeAIEmbeddings(model=_EMBEDDING_MODEL)
    return Chroma(
        collection_name=_COLLECTION_NAME,
        embedding_function=embedding_fn,
        persist_directory=_PERSIST_DIR,
    )


def _normalize_filter(raw_filter: Optional[Union[str, Dict]]) -> Optional[Dict]:
    """Normalize the filter parameter into Chroma's where_document format."""
    if raw_filter is None:
        return None
    if isinstance(raw_filter, str):
        return {"$contains": raw_filter}
    if isinstance(raw_filter, dict):
        return raw_filter
    return None


def _format_result(metadata: Dict, content: str) -> Dict:
    """Combine metadata and page_content into a single result dictionary."""
    output = dict(metadata)
    output["content"] = content
    return output


@tool
async def search_jobs(
    query: str,
    top_k: int = 5,
    where_document: Optional[Union[str, Dict]] = None,
) -> List[Dict]:
    """
    Search for relevant job postings using a natural language query.
    Use this tool to find jobs that match the candidate's skills and experience.

    Args:
        query: Search query (e.g., "Senior Python Developer with AWS experience")
        top_k: Number of results to return (default: 5)
        where_document: Optional filter for document content.
                        - If a string is provided, performs a "$contains" search (case-sensitive).
                        - If a dictionary is provided, it is passed directly as Chroma's
                          `where_document` filter.
                          Logical operators such as "$and" and "$or" are supported.
                          Example:
                          {"$and": [{"$contains": "Remote"}, {"$contains": "Python"}]}
    """
    store = _get_vector_store()

    # Build search parameters
    search_params: Dict = {"k": top_k}
    doc_filter = _normalize_filter(where_document)
    if doc_filter is not None:
        search_params["where_document"] = doc_filter

    # Perform similarity search on the vector store
    matched_docs = await store.asimilarity_search(query, **search_params)

    # Format the results for the agent
    return [_format_result(doc.metadata, doc.page_content) for doc in matched_docs]