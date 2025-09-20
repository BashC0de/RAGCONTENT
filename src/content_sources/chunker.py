"""
Semantic chunking with overlap. Uses token estimation.
We keep tokenization simple (approx tokens by words).
For production use tiktoken or tokenizer of your embedding model.
"""
from typing import List, Dict

def chunk_text(text: str, chunk_size_tokens=800, overlap=100):
    words = text.split()
    approx_tokens = len(words)
    # approximate: tokens ~= words
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size_tokens, len(words))
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start = end - overlap if end < len(words) else end
    return chunks

def semantic_chunker(doc: Dict, chunk_size=800, overlap=100):
    text = doc["text"]
    paragraphs = text.split("\n\n")
    # naive semantic: chunk per paragraph groups until size reached
    buffer = []
    buffer_len = 0
    chunks = []
    for p in paragraphs:
        p_len = len(p.split())
        if buffer_len + p_len > chunk_size and buffer:
            chunks.append(" ".join(buffer))
            buffer = [p]
            buffer_len = p_len
        else:
            buffer.append(p)
            buffer_len += p_len
    if buffer:
        chunks.append(" ".join(buffer))
    # Ensure overlap
    final = []
    for c in chunks:
        final += chunk_text(c, chunk_size_tokens=chunk_size, overlap=overlap)
    # preserve metadata
    return [{"id": f"{doc['id']}_chunk_{i}", "text": c, "metadata": doc.get("metadata", {})} for i,c in enumerate(final)]
