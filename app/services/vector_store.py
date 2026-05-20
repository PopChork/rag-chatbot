import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)

from app.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME


class VectorStore:
    def __init__(self, vector_size: int, collection_name: str | None = None):
        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT
        )
        self.collection_name = collection_name or COLLECTION_NAME
        self.vector_size = vector_size
        self._ensure_collection()

    def _ensure_collection(self):
        existing = [c.name for c in self.client.get_collections().collections]

        if self.collection_name not in existing:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

    def reset_collection(self):
        existing = [c.name for c in self.client.get_collections().collections]

        if self.collection_name in existing:
            self.client.delete_collection(
                collection_name=self.collection_name
            )

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE
            )
        )

    def upsert_chunks(self, chunks, embeddings):
        doc_id = str(uuid.uuid4())
        points = []

        for i, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())

            payload = {
                "doc_id": doc_id,
                "filename": chunk["filename"],
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "source": f"{chunk['filename']}#page={chunk['page']}"
            }

            points.append(
                PointStruct(
                    id=chunk_id,
                    vector=embeddings[i],
                    payload=payload
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )

        return doc_id

    def search(self, query_vector, top_k: int = 5, doc_id: str | None = None):
        query_filter = None

        if doc_id:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=doc_id)
                    )
                ]
            )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True
        )

        results = response.points

        return [
            {
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "filename": hit.payload.get("filename", ""),
                "page": hit.payload.get("page", None),
                "source": hit.payload.get("source", ""),
                "doc_id": hit.payload.get("doc_id", ""),
                "chunk_index": hit.payload.get("chunk_index", None)
            }
            for hit in results
        ]