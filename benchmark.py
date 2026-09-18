"""Stress / benchmark script for pdf-chat's core pipeline (chunking + retrieval).

This is a manual script, NOT a pytest test. Run it with:

    .venv/bin/python benchmark.py

It checks edge cases, non-ASCII handling, then times chunking and retrieval at
increasing sizes. The retrieval section loads the sentence-transformers model
on the first call (~80 MB download), so the first retrieval timing includes
that one-time cost.

Note: this exercises the `rag.py` layer (chunking + semantic search). The
PDF-to-text extraction step (`pypdf`) isn't stressed here because it needs
real PDF files.
"""

import time

from rag import chunk_slides, chunk_text, retrieve


def make_pages(num_pages, words_per_page=200):
    """Build synthetic `(page_number, text)` tuples of filler words."""
    pages = []
    for i in range(1, num_pages + 1):
        text = " ".join(f"word{i}_{j}" for j in range(words_per_page))
        pages.append((i, text))
    return pages


def check_edge_cases():
    """Verify empty / whitespace-only / invalid inputs degrade gracefully."""
    assert chunk_text("") == []
    assert chunk_text("   \n\t ") == []
    assert chunk_slides("d.pdf", []) == []
    assert chunk_slides("d.pdf", [(1, ""), (2, "   ")]) == []

    # overlap >= max_chars must raise, not hang.
    try:
        chunk_text("x", max_chars=5, overlap=5)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for overlap >= max_chars")

    print("[edge cases] OK")


def check_non_ascii():
    """Verify accented text (e.g. Portuguese) survives chunking."""
    text = "Olá, como você está? Ação, coração, avião, maçã, não, relação."
    chunks = chunk_text(text, max_chars=100, overlap=0)
    assert chunks and "Olá" in chunks[0]
    print("[non-ascii] OK — chunks:", chunks)


def benchmark_chunking():
    """Time chunk_slides across increasing page counts."""
    print("\n== chunking (chunk_slides) ==")
    for pages in (10, 100, 500, 2000):
        doc = make_pages(pages)
        start = time.perf_counter()
        chunks = chunk_slides("synthetic.pdf", doc)
        elapsed = time.perf_counter() - start
        print(f"  {pages:>5} pages -> {len(chunks):>6} chunks in {elapsed:.3f}s")


def benchmark_retrieval():
    """Time retrieve (embed + rank) across increasing chunk counts.

    The first call includes the one-time model load; later calls show the
    per-question cost, which scales with the number of chunks (every chunk is
    re-embedded on each query — a known limitation).
    """
    print("\n== retrieval (embed + rank) ==")
    print("  (first call loads the model — expect it to be slow)")

    # One big synthetic document, sliced down to the target chunk count.
    all_chunks = chunk_slides("synthetic.pdf", make_pages(2000, words_per_page=50))

    for n in (50, 200, 500, 1000):
        start = time.perf_counter()
        retrieve("word1_0 word1_1", all_chunks[:n], k=5)
        elapsed = time.perf_counter() - start
        print(f"  {n:>5} chunks -> top-5 in {elapsed:.3f}s")


def main():
    print("pdf-chat stress test")
    check_edge_cases()
    check_non_ascii()
    benchmark_chunking()
    benchmark_retrieval()
    print("\ndone")


if __name__ == "__main__":
    main()
