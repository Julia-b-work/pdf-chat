import numpy as np
import pytest

from rag import chunk_slides, chunk_text, cosine_similarity


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

def test_chunk_text_rejects_overlap_too_large():
    with pytest.raises(ValueError):
        chunk_text("hello world", max_chars=5, overlap=5)


def test_chunk_slides_tags_each_page():
    pages = [(1, "hello"), (2, "world")]
    assert chunk_slides("d.pdf", pages) == [
        {"doc": "d.pdf", "page": 1, "text": "hello"},
        {"doc": "d.pdf", "page": 2, "text": "world"},
    ]


def test_chunk_slides_skips_empty_pages():
    pages = [(1, ""), (2, "hello"), (3, "   ")]
    assert chunk_slides("d.pdf", pages) == [
        {"doc": "d.pdf", "page": 2, "text": "hello"},
    ]


def test_chunk_slides_subchunks_long_page():
    chunks = chunk_slides("d.pdf", [(3, "a" * 1000)], max_chars=400)
    assert len(chunks) > 1
    assert all(c["page"] == 3 for c in chunks)
    assert all(c["doc"] == "d.pdf" for c in chunks)
