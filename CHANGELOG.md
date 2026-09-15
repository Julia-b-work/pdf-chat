# Changelog

All notable changes to this project are recorded here. Versions follow
[Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH.

## [0.2.0] - 2026-09-15

### Added
- **Multi-PDF support.** Upload one or more PDFs and ask questions across all
  of them. Every chunk is tagged with its source document, so answers cite the
  document name alongside the chunk number.
- `make_chunks()` helper in `rag.py` — pure, testable document-tagging logic.
- Tests covering multi-document chunk tagging.

### Changed
- `retrieve()` now returns dicts (`{"doc", "text"}`) instead of plain strings,
  so source-document info survives retrieval.
- The generation prompt instructs Claude to cite the source document as well as
  the chunk number.
- README updated to match: intro, features, how-it-works, project structure,
  and roadmap.

## [0.1.0] - 2026-09-14

Initial release: single-PDF RAG app with PDF text extraction, fixed-window
chunking, semantic retrieval with embeddings, Claude answer generation with
citations, and a Streamlit UI. Includes a pytest suite and GitHub Actions CI.
