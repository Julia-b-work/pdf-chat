import os
import io
from dotenv import load_dotenv
from anthropic import Anthropic
from pypdf import PdfReader
import streamlit as st

from rag import chunk_text, retrieve

load_dotenv()


def generate(question, chunks):
    context = "\n\n".join(f"[{i + 1}] {chunk}" for i, chunk in enumerate(chunks))

    prompt = (
        "reply using ONLY the context below. "
        "if the answer is not in the context, say you didn't find it. "
        "cite the number of the chunk you used.\n\n"
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

uploaded = st.file_uploader("Upload a PDF", type="pdf")

if uploaded is not None:
    reader = PdfReader(io.BytesIO(uploaded.read()))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    chunks = chunk_text(text)
    st.write(f"Loaded {len(chunks)} chunks")

    question = st.text_input("Ask a question")

    if question:
        top = retrieve(question, chunks, k=5)
        with st.spinner("Thinking..."):
            answer = generate(question, top)
        st.write(answer)
