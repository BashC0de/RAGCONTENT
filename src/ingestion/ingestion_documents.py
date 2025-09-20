"""
ingestion_documents.py
----------------------
Full ingestion pipeline:
1. Load raw documents from URLs, RSS feeds, PDFs, etc.
2. Clean & preprocess text.
3. Chunk into semantic segments with overlap.
4. Generate dense (or hybrid) embeddings.
5. Upsert into the configured vector database (Pinecone / Weaviate / FAISS).
"""

from typing import List, Dict
from utils.logger import logger
from content_sources.loaders import load_from_url, load_from_rss
from ingestion.preprocess import clean_html_text
from content_sources.chunker import semantic_chunker
from embeddings.hybrid import hybrid_embeddings   # or use embeddings.embedder
from vector_database.store import upsert_vectors


# Ex ingestion sources — adapt these to your needs.

DEFAULT_URLS = [
    "https://techcrunch.com",
    "https://www.theverge.com/tech",
    "https://arstechnica.com",
    "https://www.zdnet.com",
]


DEFAULT_RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://feeds.arstechnica.com/arstechnica/index/",
    "https://www.theverge.com/rss/index.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
]



def ingest_sources(
    urls: List[str] = None,
    rss_feeds: List[str] = None,
    use_hybrid: bool = True,
    chunk_size: int = 800,
    overlap: int = 100,
) -> None:
    """
    Main entry point to ingest multiple sources and write to vector DB.
    """
    urls = urls or DEFAULT_URLS
    rss_feeds = rss_feeds or DEFAULT_RSS_FEEDS

    logger.info("Starting document ingestion pipeline...")

    all_docs: List[Dict] = []


    # Load documents from URLs

    for url in urls:
        try:
            doc = load_from_url(url)
            all_docs.append(doc)
            logger.info(f"Loaded {url}")
        except Exception as e:
            logger.warning(f"Failed to load {url}: {e}")

    # Load from RSS feeds
    for feed in rss_feeds:
        try:
            rss_docs = load_from_rss(feed)
            all_docs.extend(rss_docs)
            logger.info(f"Loaded {len(rss_docs)} entries from RSS {feed}")
        except Exception as e:
            logger.warning(f"Failed to load RSS {feed}: {e}")

    if not all_docs:
        logger.warning("No documents loaded—nothing to ingest.")
        return

    #  Chunk & Embed

    all_chunks: List[Dict] = []
    for doc in all_docs:
        chunks = semantic_chunker(doc, chunk_size=chunk_size, overlap=overlap)
        all_chunks.extend(chunks)

    texts = [c["text"] for c in all_chunks]

    logger.info(f"Created {len(all_chunks)} semantic chunks.")

    # Generate embeddings

    if use_hybrid:
        embeddings = hybrid_embeddings(texts)
    else:
        from embeddings.embedder import embed_texts
        embeddings = embed_texts(texts)

    for chunk, emb in zip(all_chunks, embeddings):
        chunk["vector"] = emb

    logger.info("Embeddings generated for all chunks.")

    #  Upsert to Vector Database

    upsert_vectors(all_chunks)
    logger.info("Upsert complete. Vector database updated.")


if __name__ == "__main__":
    # Allows: python -m content_sources.ingestion_documents
    ingest_sources()
