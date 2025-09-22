"""
Vector DB abstraction: Pinecone | Weaviate | FAISS fallback
Provides: upsert_vectors(items), query_vector(query_embedding, top_k)
Item format: {"id": id, "vector": [...], "metadata": {...}, "text": "..."}

Single, clean initialization for Pinecone / Weaviate / FAISS
"""

import os
import uuid
from typing import List, Dict
from src.config import settings
from src.utils.logger import logger
import pinecone

def init_vector_store():
    pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment="us-east1-gcp")
    # Example: create or connect to an index
    if "my-index" not in pinecone.list_indexes():
        pinecone.create_index("my-index", dimension=1536)
    index = pinecone.Index("my-index")
    return index

VECTOR_STORE: List[Dict] = []
FAISS_INDEX = None
FAISS_DOCS: List[Dict] = []

# --------------------------
# Determine which DB to use
# --------------------------
USE = "pinecone" if settings.PINECONE_API_KEY else ("weaviate" if settings.WEAVIATE_URL else "faiss")

# --------------------------
# Pinecone setup
# --------------------------
if USE == "pinecone":
    from pinecone import Pinecone, ServerlessSpec
    import os
    from src.utils.logger import logger
    from src.config import settings

    # Pinecone index config
    INDEX_NAME = "rag-index"
    region = os.getenv("PINECONE_REGION", "us-east-1")

    # Initialize Pinecone client
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)

    # Create the index if it doesn't exist
    existing_indexes = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        logger.info(f"Creating Pinecone index '{INDEX_NAME}' in region {region}...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,  # match your embedding size
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=region)
        )
        logger.info("Index created.")

    # Now get the Index handle safely
    index = pc.Index(INDEX_NAME)


# --------------------------
# Weaviate setup
# --------------------------
elif USE == "weaviate":
    import weaviate
    client = weaviate.Client(settings.WEAVIATE_URL)
    logger.info("Weaviate client initialized.")

# --------------------------
# FAISS fallback
# --------------------------
else:
    import faiss
    import numpy as np
    logger.info("Using FAISS local index as fallback.")

# --------------------------
# Common API
# --------------------------
def init_vector_store():
    """Initialize the vector store (e.g., connect to Pinecone or Weaviate)."""
    logger.info(f"Vector store initialized: {USE}")


def add_vector(embedding: List[float], metadata: Dict = None, id: str = None) -> str:
    """Store a vector embedding locally (fallback) or metadata placeholder."""
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

    elif USE == "weaviate":
        for it in items:
            client.data_object.create(
                {"text": it["text"], **it.get("metadata", {})},
                class_name="Content",
                uuid=it["id"]
            )

    else:
        global FAISS_INDEX, FAISS_DOCS
        import numpy as np
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
        return [{"id": m["id"], "score": m["score"], "metadata": m["metadata"]} for m in res["matches"]]

    elif USE == "weaviate":
        r = client.query.get("Content", ["text"]).with_near_vector({"vector": vec}).with_limit(top_k).do()
        return r

    else:
        import numpy as np
        D, I = FAISS_INDEX.search(np.array([vec]).astype("float32"), top_k)
        matches = [{"id": FAISS_DOCS[idx]["id"], "score": float(dist), "metadata": FAISS_DOCS[idx].get("metadata")} 
                   for idx, dist in zip(I[0], D[0])]
        return matches
