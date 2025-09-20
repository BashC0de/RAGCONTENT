from src.embeddings.embedder import embed_texts
from src.vector_database import store
from src.utils.logger import logger
from src.retrieval.filters import apply_filters

def retrieve_for_query(query: str, top_k=20, rerank_k=8):
    # embed query
    q_emb = embed_texts([query])[0]
    #  initial retrieve
    initial = store.query_vector(q_emb, top_k=top_k)
    # optional reranking - basic: re-embed snippets and compute cosine with query
    # For production use a learned reranker like Cohere Rerank
    candidates = []
    for m in initial:
        # load text from metadata or call back DB
        txt = m.get("metadata", {}).get("text") or m.get("text")
        candidates.append({"id": m["id"], "text": txt, "score": m["score"], "metadata": m.get("metadata", {})})
    # simple top-k
    final = sorted(candidates, key=lambda x: x["score"], reverse=False)[:rerank_k]  # if pinecone score = distance lower better
    logger.info(f"Retrieved {len(final)} documents for query.")
    return final

def retrieve_for_query(query: str, top_k=20, rerank_k=8):
    q_emb = embed_texts([query])[0]
    initial = store.query_vector(q_emb, top_k=top_k)

    # Apply filters — e.g., minimum similarity 0.75 and only research papers
    initial = apply_filters(initial,
                            min_score=0.75,
                            allowed_types=["research_paper", "blog_post"])

    # (Optional) rerank logic here…
    return initial[:rerank_k]
