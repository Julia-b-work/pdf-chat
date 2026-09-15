import numpy as np
from sentence_transformers import SentenceTransformer
import os
import io
from dotenv import load_dotenv
from anthropic import Anthropic
from pypdf import PdfReader
import streamlit as st


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

load_dotenv()


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def chunk_text(text, max_chars=400, overlap=100):
    flat = " ".join(text.split())

    chunks = []
    start = 0
    step = max_chars - overlap

    while start < len(flat):
        chunks.append(flat[start:start + max_chars])
        start += step
    return chunks


def retrieve(question, chunks, k=3):
    q_vec = model.encode(question)
    chunk_vecs = model.encode(chunks)

    scored = []

    for i, chunk in enumerate(chunks):
        score = cosine_similarity(q_vec, chunk_vecs[i])
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:k]]


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
