# Changelog

All notable changes to this project are recorded here. Versions follow
[Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH.

## [0.3.0] - 2026-09-15

### Added
- **Slide-aware chunking.** Chunks now respect page boundaries instead of
  splitting the flattened document into arbitrary windows, so a chunk never
  spans two pages. Each chunk is tagged with its source page, and answers cite
  the document and page number.
- `chunk_slides()` helper in `rag.py` — pure, testable page-aware chunking
  (skips empty pages, sub-chunks long pages).
- Tests covering page tagging, empty-page skipping, and sub-chunking.

### Changed
- `generate()` now cites the source document and page number instead of the
  document and chunk number.
- README updated to match: intro, features, how-it-works, and roadmap.

## [0.2.1] - 2026-09-15

### Fixed
- **Empty PDFs.** Scanned (image-only) PDFs previously produced zero chunks with
  no explanation; the app now warns that no text was found and names the file.
- Code-style cleanup in `rag.py` (PEP8 blank lines and spacing).

### Added
- Test for the empty-text chunking edge case.

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
