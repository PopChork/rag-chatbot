from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: list[str]):
        return self.model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()

    def embed_query(self, query: str):
        return self.model.encode(
            query,
            normalize_embeddings=True
        ).tolist()