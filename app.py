import os
import io
from dotenv import load_dotenv
from anthropic import Anthropic
from pypdf import PdfReader
import streamlit as st

from rag import chunk_slides, retrieve

load_dotenv()


def generate(question, chunks):
    context = "\n\n".join(f"[{i + 1}] ({chunk['doc']}, page {chunk['page']}) {chunk['text']}" for i, chunk in enumerate(chunks))

    prompt = (
        "reply using ONLY the context below. "
        "if the answer is not in the context, say you didn't find it. "
        "cite the document name and page number you used.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )

    api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


st.title("Chat with your PDFs")

uploaded = st.file_uploader("Upload a PDF", type="pdf", 
                            accept_multiple_files=True)

if uploaded:
    chunks = []
    empty_files = []
    for f in uploaded:
        reader = PdfReader(io.BytesIO(f.read()))
        pages = [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
        file_chunks = chunk_slides(f.name, pages)
        if not file_chunks:
            empty_files.append(f.name)
        chunks.extend(file_chunks)

    if empty_files:
        st.warning(
            f"No text found in: {', '.join(empty_files)}. "
            "This may be a scanned (image-only) PDF."
        )

    st.write(f"Loaded {len(chunks)} chunks from {len(uploaded)} file(s)")

    question = st.text_input("Ask a question")

    if question:
        top = retrieve(question, chunks, k=5)
        with st.spinner("Thinking..."):
            answer = generate(question, top)
        st.write(answer)
