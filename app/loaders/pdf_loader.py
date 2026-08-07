"""
PDF text extraction WITHOUT langchain's PyPDFLoader.

We use `pypdf` directly (page-by-page) so we control exactly how the
text and metadata are shaped before they ever reach the chunker /
embedding step. Each returned item is a plain dict:

    {"text": "<page text>", "metadata": {"source": "<file>", "page": <int>}}

Keeping this a plain dict (instead of a langchain Document) means the
rest of the pipeline (chunker, embeddings, chromadb) has zero
dependency on langchain.
"""

from pathlib import Path
from pypdf import PdfReader


class PDFLoader:

    def __init__(self, pdf_folder):
        self.pdf_folder = Path(pdf_folder)

    def list_pdfs(self):
        return sorted(self.pdf_folder.glob("*.pdf"))

    def load_all_pdfs(self):
        documents = []

        print("=" * 60)
        print("PDF Folder :", self.pdf_folder)
        print("=" * 60)

        if not self.pdf_folder.exists():
            print("PDF folder does not exist.")
            return documents

        pdf_files = self.list_pdfs()
        print("PDF Files Found:", len(pdf_files))

        if len(pdf_files) == 0:
            print("No PDF files found inside the folder.")
            return documents

        for pdf in pdf_files:
            print(f"Loading -> {pdf.name}")

            try:
                reader = PdfReader(str(pdf))
                page_count = 0

                for page_number, page in enumerate(reader.pages, start=1):
                    text = (page.extract_text() or "").strip()

                    if not text:
                        continue

                    documents.append({
                        "text": text,
                        "metadata": {
                            "source": pdf.name,
                            "page": page_number
                        }
                    })
                    page_count += 1

                print(f"Pages with text : {page_count}")

            except Exception as e:
                print(f"Error loading {pdf.name}")
                print(e)

        print("=" * 60)
        print("Total Pages Loaded :", len(documents))
        print("=" * 60)

        return documents
