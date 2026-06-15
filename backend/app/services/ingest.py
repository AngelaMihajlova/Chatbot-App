from typing import List

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI

from app.core.config import settings
from app.services import vector as vector_svc

_openai_client: OpenAI = None


def _get_openai() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def extract_text(content: bytes, mimetype: str) -> str:
    if mimetype == "application/pdf":
        doc = fitz.open(stream=content, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    return content.decode("utf-8", errors="ignore")


def chunk_text(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_text(text)


def embed_texts(texts: List[str]) -> List[List[float]]:
    client = _get_openai()
    resp = client.embeddings.create(model=settings.EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def ingest_document(document_id: str, filename: str, s3_key: str, content: bytes, mimetype: str) -> int:
    text = extract_text(content, mimetype)
    chunks = chunk_text(text)
    if not chunks:
        return 0

    batch_size = 64
    all_chunks = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        embeddings = embed_texts(batch)
        for j, (chunk, emb) in enumerate(zip(batch, embeddings)):
            all_chunks.append({
                "text": chunk,
                "embedding": emb,
                "filename": filename,
                "s3_key": s3_key,
                "chunk_idx": i + j,
            })

    vector_svc.upsert_chunks(document_id, all_chunks)
    return len(all_chunks)
