from typing import List, Tuple

from app.core.config import settings
from app.services import vector as vector_svc
from app.services.ingest import _get_openai, embed_texts


def rag_query(question: str, history: List[dict], allowed_doc_ids=None) -> Tuple[str, List[dict]]:
    query_emb = embed_texts([question])[0]
    results = vector_svc.search(query_emb, limit=5, allowed_doc_ids=allowed_doc_ids)

    context_parts = [
        f"[{i}] (from {r['filename']})\n{r['text']}"
        for i, r in enumerate(results, 1)
    ]
    context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

    system_prompt = (
        "You are a helpful assistant that answers questions based on the provided context. "
        "Cite source numbers like [1], [2] when using information from the context. "
        "If the context is insufficient, say so honestly.\n\n"
        f"Context:\n{context}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    client = _get_openai()
    response = client.chat.completions.create(model=settings.CHAT_MODEL, messages=messages)
    answer = response.choices[0].message.content

    citations = [
        {"filename": r["filename"], "text": r["text"][:300], "score": float(r["score"])}
        for r in results
    ]
    return answer, citations
