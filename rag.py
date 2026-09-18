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


def embed_chunks(chunks):
    """Embed every chunk's text once.

    This is the expensive step — it runs the embedding model over the whole
    corpus — so it should be called once per document set, not per question.
    Returns the chunk embeddings in the same order as `chunks`.
    """
    model = _load_model()
    texts = [chunk["text"] for chunk in chunks]
    return model.encode(texts)


def retrieve(question, chunks, k=3, chunk_vecs=None):
    """Return the top-`k` chunks most semantically similar to the question.

    If `chunk_vecs` (precomputed embeddings from `embed_chunks`) is given, only
    the question is embedded — fast. Otherwise the chunks are embedded too,
    which is slower but convenient for one-off calls.
    """
    model = _load_model()
    q_vec = model.encode(question)
    if chunk_vecs is None:
        chunk_vecs = model.encode([chunk["text"] for chunk in chunks])

    scored = []
    for i, chunk in enumerate(chunks):
        scored.append((cosine_similarity(q_vec, chunk_vecs[i]), chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:k]]
