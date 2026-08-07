# Government AI Chatbot — Gen AI Edition (Groq + ChromaDB + Sentence-Transformers)

This is the same citizen-facing chatbot (schemes, eligibility, application steps, CSC lookup),
rebuilt so every AI piece is explicit Gen AI plumbing instead of a LangChain/Ollama/FAISS/spaCy
black box:

| Old stack                          | New stack                                   |
|-------------------------------------|----------------------------------------------|
| LangChain `PyPDFLoader`              | raw `pypdf.PdfReader` (`app/loaders/pdf_loader.py`) |
| LangChain `RecursiveCharacterTextSplitter` | custom sentence-aware chunker (`app/loaders/chunker.py`) |
| `langchain_ollama` `OllamaEmbeddings` | `sentence-transformers` (`app/embeddings/embedding_model.py`) |
| FAISS                                | ChromaDB persistent collection (`app/embeddings/vector_store.py`) |
| `ChatOllama` (local LLM)             | Groq API — `llama-3.3-70b-versatile` (`app/models/groq_client.py`) |
| Keyword `IntentClassifier` + spaCy `SlotExtractor` | Groq few-shot (multi-shot) intent/slot classifier (`app/chatbot/intent_llm.py`) |
| `ConversationBufferMemory`           | plain `deque`-based memory (`app/chatbot/memory.py`) |

Eligibility **verdicts** stay 100% rule-based (`app/services/eligibility_service.py`) — the LLM
is only used, chain-of-thought style, to *explain* a verdict the rules already decided.

## 1. Folder hierarchy

```
Gov-AI-Chatbot-GenAI/
├── .env.example              # copy to .env and fill in GROQ_API_KEY
├── config.py                 # reads env vars, exposes Config.*
├── requirements.txt
├── run.py                    # Flask entrypoint
├── app/
│   ├── loaders/
│   │   ├── pdf_loader.py     # pypdf text extraction (NOT langchain)
│   │   ├── json_loader.py    # unchanged
│   │   └── chunker.py        # custom chunker, no langchain
│   ├── embeddings/
│   │   ├── embedding_model.py# SentenceTransformer singleton
│   │   ├── vector_store.py   # ChromaDB persistent client wrapper
│   │   └── build_index.py    # RUN THIS to (re)build the index
│   ├── models/
│   │   └── groq_client.py    # Groq chat wrapper
│   ├── chatbot/
│   │   ├── prompts.py        # RAG prompt, few-shot intent prompt, CoT explanation prompt
│   │   ├── memory.py         # per-session conversation history
│   │   ├── rag.py            # retrieval (Chroma) + generation (Groq)
│   │   └── intent_llm.py     # few-shot intent + slot extraction via Groq
│   ├── services/
│   │   ├── scheme_service.py     # wraps GovernmentRAG
│   │   ├── eligibility_service.py# deterministic rules + optional CoT explanation
│   │   └── csc_locator.py        # unchanged, JSON lookup
│   ├── api/
│   │   ├── routes.py, controller.py, schemas.py
│   └── database/              # schemes.json, csc_centers.json, eligibility_rules.json
├── data/
│   ├── pdfs/                  # source scheme PDFs
│   └── chroma_store/          # created on first index build (gitignored)
└── frontend/streamlit_app.py   # unchanged citizen-facing chat UI
```

## 2. Execution sequence

```bash
# 1) install dependencies
pip install -r requirements.txt

# 2) configure your key
cp .env.example .env
# edit .env -> GROQ_API_KEY=<your key>

# 3) build the vector index (PDF -> chunks -> embeddings -> ChromaDB)
python -m app.embeddings.build_index

# 4) start the API
python run.py                       # Flask on :5000

# 5) in a second terminal, start the citizen-facing UI
streamlit run frontend/streamlit_app.py
```

Re-run step 3 any time you add/replace files in `data/pdfs/`.

## 3. What each Gen AI concept maps to (for your write-up)

- **Prompting techniques** (from your `2_one_shot`, `3_multi_shot`, `4_chain_of_thoughts` samples):
  - One/multi-shot -> `INTENT_PROMPT` in `prompts.py` (few-shot intent+slot classification).
  - Chain-of-thought -> `ELIGIBILITY_EXPLANATION_PROMPT` (step-by-step verdict explanation).
  - Grounded RAG prompt -> `RAG_PROMPT` (context + conversation history + question).
- **Sentence embeddings** (`5_Sentence_Embeddings...py`) -> `app/embeddings/embedding_model.py`,
  used both when indexing (`build_index.py`) and at query time (`vector_store.py`).
- **ChromaDB** (`6_chromadb_vector_store...py`) -> `app/embeddings/vector_store.py`, a persistent
  collection storing scheme-PDF chunks with cosine similarity search.
- **Groq** (`1_groq_connection_test.py`) -> `app/models/groq_client.py`, the single place every
  LLM call goes through.

## 4. Security note

The sample scripts you shared had a real Groq API key hardcoded in plaintext. That key should be
treated as compromised — revoke/regenerate it in the Groq console and use `.env` (already
`.gitignore`d) instead, as this project does via `Config.GROQ_API_KEY`.
