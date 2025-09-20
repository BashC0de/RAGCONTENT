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
def retrieve_context_documents(query: str):
    # TODO: Replace with actual RAG retrieval
    return ["Document 1 text...", "Document 2 text..."]
 

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

