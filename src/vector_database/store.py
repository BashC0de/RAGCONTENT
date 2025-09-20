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

# Pinecone client
if USE == "pinecone":
    import pinecone
    pinecone.init(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENV)
    INDEX_NAME = "content-index"
    if INDEX_NAME not in pinecone.list_indexes():
        pinecone.create_index(INDEX_NAME, dimension=1536)
    index = pinecone.Index(INDEX_NAME)
elif USE == "weaviate":
    import weaviate
    client = weaviate.Client(settings.WEAVIATE_URL)
    # TODO: create schema if missing
else:
    # FAISS fallback
    import faiss
    import numpy as np
    FAISS_INDEX = None
    FAISS_DOCS = []  # store metadata locally
# store.py
def init_vector_store():
    """
    Initialize the vector store (e.g., connect to Pinecone or Weaviate).
    """
    print("Vector store initialized")
    # Add your DB init logic here
VECTOR_STORE: List[Dict] = []

def add_vector(embedding: List[float], metadata: Dict = None, id: str = None) -> str:
    """
    Store a vector embedding with optional metadata.
    
    Args:
        embedding (List[float]): Vector representation of the text.
        metadata (Dict, optional): Any metadata (e.g., text, source_url, type)
        id (str, optional): If not provided, a UUID will be generated.
        
    Returns:
        str: The ID of the stored vector.
    """
    vector_id = id or str(uuid.uuid4())
    VECTOR_STORE.append({
        "id": vector_id,
        "embedding": embedding,
        "metadata": metadata or {}
    })
    return vector_id

def upsert_vectors(items):
    """
    items: list of {"id","vector","metadata","text"}
    """
    if USE == "pinecone":
        vectors = [(it["id"], it["vector"], it.get("metadata", {})) for it in items]
        index.upsert(vectors)
        return True
    elif USE == "weaviate":
        for it in items:
            client.data_object.create({"text": it["text"], **it.get("metadata", {})}, class_name="Content", uuid=it["id"])
        return True
    else:
        global FAISS_INDEX, FAISS_DOCS
        import numpy as np
        vecs = np.array([it["vector"] for it in items]).astype("float32")
        if FAISS_INDEX is None:
            FAISS_INDEX = faiss.IndexFlatL2(vecs.shape[1])
        FAISS_INDEX.add(vecs)
        FAISS_DOCS += items
        return True

def query_vector(vec, top_k=5):
    if USE == "pinecone":
        res = index.query(vec, top_k=top_k, include_metadata=True, include_values=False)
        matches = []
        for m in res["matches"]:
            matches.append({"id": m["id"], "score": m["score"], "metadata": m["metadata"]})
        return matches
    elif USE == "weaviate":
        r = client.query.get("Content", ["text"]).with_near_vector({"vector": vec}).with_limit(top_k).do()
        # parse...
        return r
    else:
        import numpy as np
        D, I = FAISS_INDEX.search(np.array([vec]).astype("float32"), top_k)
        matches = []
        for idx, dist in zip(I[0], D[0]):
            item = FAISS_DOCS[idx]
            matches.append({"id": item["id"], "score": float(dist), "metadata": item.get("metadata")})
        return matches
