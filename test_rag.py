import numpy as np

from rag import chunk_text, cosine_similarity, make_chunks


def test_chunk_short_text_is_single_chunk():
    assert chunk_text("hello world") == ["hello world"]


def test_chunk_splits_long_text():
    text = "a" * 2000
    chunks = chunk_text(text, max_chars=400, overlap=100)
    assert len(chunks) == 7


def test_every_chunk_is_within_max_chars():
    text = "word " * 1000
    chunks = chunk_text(text, max_chars=400, overlap=100)
    assert all(len(chunk) <= 400 for chunk in chunks)


def test_chunks_overlap():
    text = "a" * 1000
    chunks = chunk_text(text, max_chars=400, overlap=100)
    assert chunks[0][-100:] == chunks[1][:100]


def test_cosine_similarity_identical_is_one():
    a = np.array([1.0, 0.0, 0.0])
    assert cosine_similarity(a, a) == 1.0


def test_cosine_similarity_orthogonal_is_zero():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert abs(cosine_similarity(a, b)) < 1e-9

def test_make_chunks_tags_short_text():
    assert make_chunks("doc.pdf", "hello world") == [
        {"doc": "doc.pdf", "text": "hello world"}
    ]


def test_make_chunks_tags_every_chunk_of_long_text():
    chunks = make_chunks("doc.pdf", "a" * 1000)
    assert len(chunks) > 1
    assert all(c["doc"] == "doc.pdf" for c in chunks)
    assert all("text" in c for c in chunks)


def test_make_chunks_empty_text_returns_empty_list():
    assert make_chunks("doc.pdf", "") == []
