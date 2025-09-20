"""
Embedding interface: supports OpenAI and Cohere (and local fallbacks).
Generates dense embeddings for text.
"""
from typing import List
from src.config import settings
from src.utils.logger import logger

# import provider libs
try:
    import openai
except Exception:
    openai = None

try:
    import cohere
except Exception:
    cohere = None

def embed_texts(texts: List[str]) -> List[List[float]]:
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "openai" and openai:
        openai.api_key = settings.OPENAI_API_KEY
        resp = openai.Embedding.create(model="text-embedding-3-large", input=texts)
        return [r["embedding"] for r in resp["data"]]
    if provider == "cohere" and cohere:
        client = cohere.Client(settings.COHERE_API_KEY)
        resp = client.embed(model="embed-english-v2.0", texts=texts)
        return resp.embeddings
    # fallback
    import numpy as np
    logger.warning("Using random fallback embeddings. Set OPENAI_API_KEY or COHERE_API_KEY for real embeddings.")
    return [np.random.rand(1536).tolist() for _ in texts]
