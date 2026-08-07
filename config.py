import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:

    BASE_DIR = BASE_DIR

    PDF_FOLDER = BASE_DIR / "data" / "pdfs"

    JSON_FOLDER = BASE_DIR / "app" / "database"

    # --- Gen AI stack ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    CHROMA_DB_PATH = BASE_DIR / os.getenv("CHROMA_DB_PATH", "data/chroma_store")
    CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "gov_schemes")

    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")

    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
