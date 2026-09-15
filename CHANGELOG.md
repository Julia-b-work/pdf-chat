# Changelog

All notable changes to this project are documented in this file.

## [0.2.0] - 2026-09-15

### Added

- Multi-PDF support: upload one or more PDFs and ask questions across all of them.
- Each retrieved chunk is tagged with its source document, so answers cite the
  document name alongside the chunk number.
- New `make_chunks()` helper in `rag.py` — pure, testable document-tagging logic.
- New tests covering multi-document chunk tagging.

### Changed

- `retrieve()` now returns dicts (`{"doc", "text"}`) instead of plain strings.
- The prompt instructs Claude to cite the source document as well as the chunk.

## [0.1.0] - 2026-09-14

### Added

- Initial release: single-PDF RAG app.
- PDF text extraction, fixed-window chunking, semantic retrieval with embeddings,
  Claude answer generation with citations, and a Streamlit UI.
- pytest test suite and GitHub Actions CI.
