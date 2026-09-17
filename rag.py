"""Retrieval-augmented-generation helpers: chunking and semantic search."""

import numpy as np


def cosine_similarity(a, b):
    """Cosine similarity between two vectors (1.0 = identical, 0.0 = orthogonal)."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def chunk_text(text, max_chars=400, overlap=100):
    """Split text into fixed-size windows with overlap.

    Whitespace is flattened first (so chunks hold whole words, not line breaks),
    then the text is cut into `max_chars` windows that step by `max_chars - overlap`.
    """
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars")

    flat = " ".join(text.split())
    chunks = []
    start = 0
    step = max_chars - overlap
    while start < len(flat):
        chunks.append(flat[start:start + max_chars])
        start += step
    return chunks


def chunk_slides(doc_name, pages, max_chars=400):
    """Chunk a document page-by-page (slide-aware).

    `pages` is a list of `(page_number, page_text)` tuples. Each page is chunked
    independently (no cross-page windows) and every chunk is tagged with its
    source document and page. Empty pages are skipped.
    """
    chunks = []
    for page_num, page_text in pages:
        for text in chunk_text(page_text, max_chars=max_chars, overlap=0):
            chunks.append({"doc": doc_name, "page": page_num, "text": text})
    return chunks


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
    """Return the top-`k` chunks most semantically similar to the question.

    Both the question and every chunk are embedded, then ranked by cosine
    similarity. Returns the full chunk dicts (doc + page + text) so citations
    can name the source.
    """
    texts = [chunk["text"] for chunk in chunks]
    model = _load_model()
    q_vec = model.encode(question)
    chunk_vecs = model.encode(texts)

    scored = []
    for i, chunk in enumerate(chunks):
        scored.append((cosine_similarity(q_vec, chunk_vecs[i]), chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:k]]
