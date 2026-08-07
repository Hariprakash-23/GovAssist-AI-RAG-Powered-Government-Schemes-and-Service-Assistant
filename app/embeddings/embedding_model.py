"""
Sentence-Transformers embedding model, singleton-loaded (same idea as
the sample `5. Sentence Embeddings Using Sentence Transformers.py`).
"""

from sentence_transformers import SentenceTransformer
from config import Config


class EmbeddingModel:

    _instance = None

    @classmethod
    def get_model(cls):
        if cls._instance is None:
            print("=" * 60)
            print("Loading Sentence-Transformer model:", Config.EMBEDDING_MODEL)
            print("=" * 60)

            cls._instance = SentenceTransformer(Config.EMBEDDING_MODEL)

        return cls._instance

    @classmethod
    def encode(cls, texts):
        """texts: str or list[str] -> list[list[float]] (or single vector)"""
        model = cls.get_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
