"""
Vector DB abstraction: Pinecone | Weaviate | FAISS fallback
Provides: upsert_vectors(items), query_vector(query_embedding, top_k)
Item format: {"id": id, "vector": [...], "metadata": {...}, "text": "..."}
"""

from src.config import settings
from src.utils.logger import logger
from typing import List, Dict
import uuid

USE = "pinecone" if settings.PINECONE_API_KEY else ("weaviate" if settings.WEAVIATE_URL else "faiss")

# Global variables
VECTOR_STORE: List[Dict] = []

# Pinecone client setup
if USE == "pinecone":
    from pinecone import Pinecone, ServerlessSpec

    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    INDEX_NAME = "content-index"

    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,  # set your embedding size
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-west-2")
        )

    index = pc.index(INDEX_NAME)

# Weaviate setup
elif USE == "weaviate":
    import weaviate
    client = weaviate.Client(settings.WEAVIATE_URL)
    # TODO: create schema if missing

# FAISS fallback
else:
    import faiss
    import numpy as np
    FAISS_INDEX = None
    FAISS_DOCS = []

def init_vector_store():
    """Initialize the vector store (e.g., connect to Pinecone or Weaviate)."""
    logger.info(f"Vector store initialized: {USE}")

def add_vector(embedding: List[float], metadata: Dict = None, id: str = None) -> str:
    """Store a vector embedding with optional metadata."""
    vector_id = id or str(uuid.uuid4())
    VECTOR_STORE.append({
        "id": vector_id,
        "embedding": embedding,
        "metadata": metadata or {}
    })
    return vector_id

def upsert_vectors(items: List[Dict]):
    """Upsert a list of vectors to the selected vector DB."""
    if USE == "pinecone":
        vectors = [(it["id"], it["vector"], it.get("metadata", {})) for it in items]
        index.upsert(vectors)
        return True
    elif USE == "weaviate":
        for it in items:
            client.data_object.create(
                {"text": it["text"], **it.get("metadata", {})},
                class_name="Content",
                uuid=it["id"]
            )
        return True
    else:
        global FAISS_INDEX, FAISS_DOCS
        vecs = np.array([it["vector"] for it in items]).astype("float32")
        if FAISS_INDEX is None:
            FAISS_INDEX = faiss.IndexFlatL2(vecs.shape[1])
        FAISS_INDEX.add(vecs)
        FAISS_DOCS += items
        return True

def query_vector(vec: List[float], top_k=5):
    """Query the top_k nearest vectors from the selected vector DB."""
    if USE == "pinecone":
        res = index.query(vec, top_k=top_k, include_metadata=True, include_values=False)
        matches = [{"id": m["id"], "score": m["score"], "metadata": m["metadata"]} for m in res["matches"]]
        return matches
    elif USE == "weaviate":
        r = client.query.get("Content", ["text"]).with_near_vector({"vector": vec}).with_limit(top_k).do()
        return r  # parse as needed
    else:
        import numpy as np
        D, I = FAISS_INDEX.search(np.array([vec]).astype("float32"), top_k)
        matches = []
        for idx, dist in zip(I[0], D[0]):
            item = FAISS_DOCS[idx]
            matches.append({"id": item["id"], "score": float(dist), "metadata": item.get("metadata")})
        return matches
