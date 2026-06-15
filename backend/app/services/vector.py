import uuid
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.config import settings

_client: Optional[QdrantClient] = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.QDRANT_URL, timeout=10)
    return _client


def ensure_collection() -> None:
    qdrant = get_qdrant()
    existing = [c.name for c in qdrant.get_collections().collections]
    if settings.QDRANT_COLLECTION not in existing:
        qdrant.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
        )


def upsert_chunks(document_id: str, chunks: List[dict]) -> None:
    qdrant = get_qdrant()
    points = [
        models.PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{document_id}#{c['chunk_idx']}")),
            vector=c["embedding"],
            payload={
                "document_id": document_id,
                "filename": c["filename"],
                "s3_key": c["s3_key"],
                "chunk_idx": c["chunk_idx"],
                "text": c["text"],
            },
        )
        for c in chunks
    ]
    qdrant.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)


def delete_document_chunks(document_id: str) -> None:
    qdrant = get_qdrant()
    qdrant.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id),
                )]
            )
        ),
    )


def search(query_embedding: List[float], limit: int = 5, allowed_doc_ids: Optional[List[str]] = None) -> List[dict]:
    if allowed_doc_ids is not None and len(allowed_doc_ids) == 0:
        return []
    qdrant = get_qdrant()
    query_filter = None
    if allowed_doc_ids is not None:
        query_filter = models.Filter(
            must=[models.FieldCondition(
                key="document_id",
                match=models.MatchAny(any=allowed_doc_ids),
            )]
        )
    results = qdrant.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_embedding,
        limit=limit,
        query_filter=query_filter,
    ).points
    return [
        {
            "filename": r.payload["filename"],
            "text": r.payload["text"],
            "score": r.score,
            "document_id": r.payload.get("document_id"),
        }
        for r in results
    ]
