import os
import io
from dotenv import load_dotenv
from anthropic import Anthropic
from pypdf import PdfReader
import streamlit as st

load_dotenv()


def chunk_text(text, max_chars=800, overlap=100):
    flat = " ".join(text.split())

    chunks = []
    start = 0
    step = max_chars - overlap

    while start < len(flat):
        chunks.append(flat[start:start + max_chars])
        start += step
    return chunks


def retrieve(question, chunks, k=3):
    q_words = set(question.lower().split())

    scored = []

    for i, chunk in enumerate(chunks):
        c_words = set(chunk.lower().split())
        overlap = len(q_words & c_words)
        scored.append((overlap, i, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, _, chunk in scored[:k]]


def generate(question, chunks):
    context = "\n\n".join(f"[{i + 1}] {chunk}" for i, chunk in enumerate(chunks))

    prompt = (
            "reply using ONLY the context below. "
            "if the answer is not in the context, say you didn't find it. "
            "cite the number of the chunk you used.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}"
    )

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
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
        top = retrieve(question, chunks)
        with st.spinner("Thinking..."):
            answer = generate(question, top)
        st.write(answer)
