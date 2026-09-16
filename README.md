# Chat with Your PDFs

A retrieval-augmented-generation (RAG) web app that answers questions about one
or more documents. Upload PDFs, ask a question, and get an answer grounded in
the documents' content — with citations to the source document and page.

Built with Python, Streamlit, and the Claude API.

**Current version: 0.3.0** — see [CHANGELOG.md](CHANGELOG.md).

## Features

- **Upload one or more PDFs** and ask questions across all of them in plain language.
- **Grounded answers** — Claude is instructed to answer *only* from the
  document and to say when it can't find the answer, so it doesn't hallucinate.
- **Cited responses** — every answer references the source document and page it used.
- **Clean, minimal UI** built with Streamlit.
- **Free to deploy** on Streamlit Cloud.

## How it works

The app implements a classic RAG pipeline:

1. **Extract** — pull raw text out of each PDF with `pypdf`.
2. **Chunk** — split each page into ~400-character windows, so every chunk is
   slide-aware and tagged with its source document and page number.
3. **Retrieve** — embed the question and every chunk with a sentence-transformer
   model, then return the top 5 most *semantically* similar chunks.
4. **Generate** — hand those chunks + the question to Claude with a
   "answer only from context, cite the source" prompt.

Retrieval uses **semantic search with embeddings** (`all-MiniLM-L6-v2`), which
matches meaning rather than exact wording — so synonyms, accents, and phrasing
variations are handled correctly.

## Tech stack

- **Python 3**
- **Streamlit** — UI
- **pypdf** — PDF text extraction
- **sentence-transformers** — embeddings for semantic retrieval
- **Anthropic Claude API** — answer generation
- **python-dotenv** — local secrets management

## Getting started

### 1. Clone and set up

```bash
git clone https://github.com/Julia-b-work/pdf-chat.git
cd pdf-chat
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Add your API key

Create a `.env` file (never commit it):

```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 3. Run

```bash
streamlit run app.py
```

Then open the printed URL, upload a PDF, and ask a question.

## Deployment

The app deploys for free on [Streamlit Cloud](https://share.streamlit.io):

1. Push this repo to GitHub.
2. On Streamlit Cloud, create a **New app** from the repo (`app.py` as main file).
3. Add the secret in **Settings → Secrets** (TOML format):

```
ANTHROPIC_API_KEY = "sk-ant-api03-..."
```

The app reads `st.secrets` on the cloud and falls back to `.env` locally, so the
same code works in both environments.

## Project structure

```
.
├── app.py             # the Streamlit app (RAG pipeline + UI)
├── rag.py             # chunking, retrieval, and document-tagging logic
├── test_rag.py        # tests for chunking and retrieval helpers
├── extract.py         # standalone script: print a PDF's extracted text
├── requirements.txt   # Python dependencies
├── .env               # API key (gitignored)
└── .gitignore
```

## Roadmap

- [x] PDF text extraction
- [x] Fixed-window chunking
- [x] Semantic retrieval with embeddings
- [x] Claude answer generation with citations
- [x] Streamlit UI
- [x] Slide-aware chunking (split by page, not character count)
- [x] Multi-PDF support
- [ ] Streaming responses for long documents
