"""
Very basic skeleton for hybrid embeddings (dense + sparse).
Dense computed with embedder; sparse with TF-IDF vectorizer.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from .embedder import embed_texts

tfidf = TfidfVectorizer(max_features=1024)

def build_sparse_vectors(doc_texts):
    X = tfidf.fit_transform(doc_texts)
    return X.toarray().tolist()

def hybrid_embeddings(texts):
    dense = embed_texts(texts)
    sparse = build_sparse_vectors(texts)
    # concatenate
    hybrids = [d + s for d,s in zip(dense, sparse)]
    return hybrids
