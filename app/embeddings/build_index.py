"""
One-shot indexing script. Run this whenever you add/change source
PDFs or JSON scheme data:

    python -m app.embeddings.build_index

Pipeline: PDFLoader -> DocumentChunker -> EmbeddingModel -> VectorStore
(replaces the old create_embeddings.py / load_vector_db.py pair).
"""

from config import Config
from app.loaders.pdf_loader import PDFLoader
from app.loaders.chunker import DocumentChunker
from app.embeddings.vector_store import VectorStore


def build():
    documents = PDFLoader(Config.PDF_FOLDER).load_all_pdfs()

    chunks = DocumentChunker(chunk_size=800, chunk_overlap=150).split_documents(documents)

    if not chunks:
        raise SystemExit("No chunks produced — check data/pdfs contains readable PDFs.")

    VectorStore.get_collection(reset=True)   # fresh collection each rebuild
    VectorStore.add_chunks(chunks)


if __name__ == "__main__":
    build()
