"""
Lightweight, dependency-free text chunker (replaces langchain's
RecursiveCharacterTextSplitter).

Splits on paragraph/sentence boundaries where possible and falls back
to a hard character split, with a configurable overlap so semantic
context isn't lost at chunk edges.
"""

import re


class DocumentChunker:

    def __init__(self, chunk_size=800, chunk_overlap=150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_into_sentences(self, text):
        # Simple sentence-ish splitter; good enough for scheme PDFs.
        pieces = re.split(r"(?<=[.!?])\s+", text.strip())
        return [p for p in pieces if p]

    def _chunk_text(self, text):
        sentences = self._split_into_sentences(text)
        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= self.chunk_size:
                current = f"{current} {sentence}".strip()
            else:
                if current:
                    chunks.append(current)

                # carry overlap forward from the end of the last chunk
                overlap_text = current[-self.chunk_overlap:] if current else ""
                current = f"{overlap_text} {sentence}".strip()

        if current:
            chunks.append(current)

        # Fallback: if a single sentence is longer than chunk_size,
        # hard-split it so nothing is ever dropped.
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                for i in range(0, len(chunk), self.chunk_size - self.chunk_overlap):
                    final_chunks.append(chunk[i:i + self.chunk_size])

        return final_chunks

    def split_documents(self, documents):
        """
        documents: list of {"text": str, "metadata": dict}  (see PDFLoader)
        returns:   list of {"text": str, "metadata": dict}  (one per chunk)
        """
        if len(documents) == 0:
            print("No documents available for chunking.")
            return []

        chunks = []

        for doc in documents:
            for piece in self._chunk_text(doc["text"]):
                chunks.append({
                    "text": piece,
                    "metadata": dict(doc["metadata"])
                })

        print("=" * 60)
        print("Chunks Created :", len(chunks))
        print("=" * 60)

        return chunks
