"""Chat with your PDFs: a RAG web app (Streamlit + Claude).

Upload one or more PDFs, ask questions, and get grounded answers with
citations to the source document and page.
"""

import os
import io
from dotenv import load_dotenv
from anthropic import Anthropic
from pypdf import PdfReader
import streamlit as st

from rag import chunk_slides, retrieve

load_dotenv()


def generate(question, chunks, history=None):
    """Stream a grounded answer from Claude.

    `chunks` are the retrieved context; `history` is the prior conversation as
    a list of `{"role", "content"}` dicts, so follow-up questions work.
    Yields the answer text chunk by chunk for streaming.
    """
    context = "\n\n".join(f"[{i + 1}] ({chunk['doc']}, page {chunk['page']}) {chunk['text']}" for i, chunk in enumerate(chunks))

    prompt = (
        "reply using ONLY the context below. "
        "if the answer is not in the context, say you didn't find it. "
        "cite the document name and page number you used.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )

    # Send the last few turns as prior messages, then the current question
    # (with fresh context) as the final user message.
    messages = [{"role": m["role"], "content": m["content"]} for m in (history or [])[-8:]]
    messages.append({"role": "user", "content": prompt})

    api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=api_key)
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


st.title("Chat with your PDFs")

uploaded = st.file_uploader("Upload a PDF", type="pdf", accept_multiple_files=True)

if uploaded:
    # Re-extract only when the uploaded files actually change (detected by
    # name + size), so each new question doesn't re-read every PDF.
    signature = tuple((f.name, f.size) for f in uploaded)

    if st.session_state.get("signature") != signature:
        chunks = []
        empty_files = []
        for f in uploaded:
            reader = PdfReader(io.BytesIO(f.read()))
            pages = [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
            file_chunks = chunk_slides(f.name, pages)
            if not file_chunks:
                empty_files.append(f.name)
            chunks.extend(file_chunks)

        st.session_state["signature"] = signature
        st.session_state["chunks"] = chunks
        st.session_state["empty_files"] = empty_files
        st.session_state["messages"] = []  # new documents -> fresh conversation
    else:
        chunks = st.session_state["chunks"]
        empty_files = st.session_state["empty_files"]

    # No text at all (all-scanned PDFs): nothing to search.
    if not chunks:
        st.error("No text could be extracted from these PDFs — they may be scanned images.")
        st.stop()

    # Some files produced no text: warn but keep the usable ones.
    if empty_files:
        st.warning(
            f"No text found in: {', '.join(empty_files)}. "
            "This may be a scanned (image-only) PDF."
        )

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    st.write(f"Loaded {len(chunks)} chunks from {len(uploaded)} file(s)")

    # Render the chat history.
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Ask a question about your PDFs")

    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                top = retrieve(prompt, st.session_state["chunks"], k=5)
                answer = st.write_stream(generate(prompt, top, st.session_state["messages"][:-1]))
                with st.expander("Sources"):
                    for i, chunk in enumerate(top):
                        st.write(f"[{i + 1}] {chunk['doc']}, page {chunk['page']}")

        st.session_state["messages"].append({"role": "assistant", "content": answer})
