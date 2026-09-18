# Changelog

All notable changes to this project are recorded here. Versions follow
[Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH.

## [0.5.1] - 2026-09-18

### Changed
- **Cached embeddings.** Chunk embeddings are now computed once (when files
  load) and reused across questions, instead of re-embedding the whole corpus
  on every query. Retrieval is roughly 1000x faster per question on large PDFs;
  the one-time indexing cost moves to upload time.
- `rag.py` gains `embed_chunks()`; `retrieve()` accepts precomputed embeddings.

### Added
- `benchmark.py` — a stress/benchmark script for chunking and retrieval.

## [0.5.0] - 2026-09-17

### Added
- **Chat interface.** Replaced the single-question form with a full chat UI
  (`st.chat_message` / `st.chat_input`) that keeps the conversation history.
- **Conversation memory.** Follow-up questions work — the last few turns are
  sent to Claude as prior messages (capped at 8).
- **Visible sources.** Each answer lists the retrieved chunks (document + page)
  in a collapsible "Sources" section.
- A "Thinking..." spinner while the answer is being retrieved and generated.

### Changed
- Chunking now runs only when the uploaded files change (via a filename/size
  signature) instead of on every question.
- `generate()` accepts prior conversation history.
- `chunk_text()` raises on an invalid `overlap` (was a silent infinite loop).
- Removed the unused `make_chunks()` helper.
- Code is now documented with docstrings and inline comments.

## [0.4.0] - 2026-09-17

### Changed
- **Streaming responses.** Answers now appear token-by-token as Claude generates
  them (via `st.write_stream`) instead of waiting behind a spinner.
- `generate()` is now a generator that yields text chunks from
  `client.messages.stream`.
- README updated to match: features and roadmap.

## [0.3.0] - 2026-09-16

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
