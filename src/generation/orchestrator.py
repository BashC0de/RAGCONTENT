# ✅ Correct
from src.retrieval.retriever import retrieve_for_query

from src.generation_pipeline.generator import generate_content
from src.utils.logger import logger

def run_rag_pipeline(request_payload: dict):
    """
    request_payload example:
    {
      "content_request": { ... },
      "generation_config": {"model":"claude-sonnet-4","temperature":0.8,"max_retrieval_docs":8}
    }
    """
    query_text = request_payload["content_request"]["topic"]
    max_docs = request_payload["generation_config"].get("max_retrieval_docs", 8)

    #  initial retrieval (multi-stage)
    initial = retrieve_for_query(query_text, top_k=20, rerank_k=max_docs)

    # build context docs (we assume retriever returns text)
    context_docs = initial  # in practice you would fetch full text
    # call generator
    result = generate_content(request_payload["content_request"], context_docs, request_payload["generation_config"])
    logger.info("RAG pipeline completed.")
    return result
from src.generation_pipeline.postprocess import postprocess_generated
from pinecone import Pinecone
from openai import OpenAI
import os

# init clients
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("rag-index")       # change to your index name
openai_client = OpenAI()

def _embed(text: str) -> list[float]:
    """Get dense vector for a query using OpenAI embeddings."""
    resp = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    return resp.data[0].embedding

def retrieve_context_documents(query: str, top_k: int = 5) -> list[str]:
    """
    Retrieve top_k most relevant docs for the query from Pinecone.
    Returns a list of document texts.
    """
    query_vec = _embed(query)

    results = index.query(
        vector=query_vec,
        top_k=top_k,
        include_metadata=True
    )

    # pull the stored text field from metadata
    return [match["metadata"].get("text", "") for match in results["matches"]]

 

def run_rag_pipeline(request_payload: dict):
    # Retrieve context documents from your Vector DB / knowledge base
    context_docs = retrieve_context_documents(
        request_payload["content_request"]["query"]
    )

    # Generate content using the retrieved docs
    raw = generate_content(
        request_payload["content_request"],
        context_docs,
        request_payload["generation_config"]
    )

    # Postprocess the generated content
    processed = postprocess_generated(
        raw,
        seo_keywords=request_payload["content_request"].get("seo_keywords"),
        run_factual_check=True,
        run_plagiarism=True
    )

    return processed

