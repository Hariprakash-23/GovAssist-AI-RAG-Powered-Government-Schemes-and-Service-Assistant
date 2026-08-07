"""
ChromaDB persistent vector store (replaces FAISS + langchain FAISS
wrapper). We compute embeddings ourselves via EmbeddingModel and hand
them to Chroma explicitly (rather than letting Chroma call an
embedding function internally) so the embedding step stays visible
and swappable.
"""

import chromadb
from config import Config
from app.embeddings.embedding_model import EmbeddingModel


class VectorStore:

    _client = None
    _collection = None

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            Config.CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
            cls._client = chromadb.PersistentClient(path=str(Config.CHROMA_DB_PATH))
        return cls._client

    @classmethod
    def get_collection(cls, reset=False):
        client = cls._get_client()

        if reset:
            try:
                client.delete_collection(Config.CHROMA_COLLECTION)
            except Exception:
                pass

        cls._collection = client.get_or_create_collection(
            name=Config.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
        return cls._collection

    @classmethod
    def add_chunks(cls, chunks, batch_size=64):
        """
        chunks: list of {"text": str, "metadata": dict}
        Embeds in batches with SentenceTransformer, then upserts into Chroma.
        """
        collection = cls.get_collection()

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]

            texts = [c["text"] for c in batch]
            metadatas = [c["metadata"] for c in batch]
            ids = [f"chunk-{start + i}" for i in range(len(batch))]

            embeddings = EmbeddingModel.encode(texts)

            collection.upsert(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings
            )

        print("=" * 60)
        print(f"Stored {len(chunks)} chunks in ChromaDB at {Config.CHROMA_DB_PATH}")
        print("=" * 60)

    @classmethod
    def similarity_search(cls, query, k=4):
        collection = cls.get_collection()

        query_embedding = EmbeddingModel.encode(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        docs = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for text, meta, dist in zip(documents, metadatas, distances):
            docs.append({
                "text": text,
                "metadata": meta,
                "distance": dist
            })

        return docs
