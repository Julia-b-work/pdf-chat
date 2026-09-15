import numpy as np


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def chunk_text(text, max_chars=400, overlap=100):
    flat = " ".join(text.split())
    chunks = []
    start = 0
    step = max_chars - overlap
    while start < len(flat):
        chunks.append(flat[start:start + max_chars])
        start += step
    return chunks


def make_chunks(doc_name, text):
    return [{"doc": doc_name, "text": ch} for ch in chunk_text(text)]

_model = None


def _load_model():
    # Imported lazily so importing rag.py (e.g. in tests) stays fast and does
    # not require the heavy sentence-transformers dependency.
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def retrieve(question, chunks, k=3):
    texts = [chunk["text"] for chunk in chunks]
    model = _load_model()
    q_vec = model.encode(question)
    chunk_vecs = model.encode(texts)

    scored = []
    for i, chunk in enumerate(chunks):
        scored.append((cosine_similarity(q_vec, chunk_vecs[i]), chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:k]]
