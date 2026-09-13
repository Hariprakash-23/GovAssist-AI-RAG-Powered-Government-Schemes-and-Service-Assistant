# GovAssist AI — RAG-Powered Government Services Assistant

GovAssist AI is a **Retrieval-Augmented Generation (RAG) based Government Services Assistant** that helps citizens retrieve information about government schemes, eligibility, required documents, application procedures, benefits, and Common Service Centre (CSC) locations.

The system processes government scheme information from PDF knowledge bases, converts the extracted content into semantic embeddings using **Sentence Transformers**, stores them in a persistent **ChromaDB** vector database, and retrieves the most relevant information using **semantic similarity search**.

Retrieved context is then provided to **Groq-powered LLMs** to generate grounded and conversational responses.

---

## Features

* Government scheme information retrieval from PDF knowledge bases
* PDF text extraction using `pypdf`
* Sentence-aware document chunking with overlap
* Semantic embeddings using Sentence Transformers
* Persistent vector storage using ChromaDB
* Cosine similarity-based semantic search
* RAG-based response generation using Groq
* LLM-based intent classification
* Scheme and location slot extraction
* Conversation memory using session-based history
* Deterministic eligibility evaluation
* Step-by-step eligibility explanation using GenAI
* CSC centre lookup using a JSON database
* Flask REST API backend
* Streamlit conversational frontend
* Environment-based API key management

---

## System Architecture

```text
                    Government Scheme PDFs
                            │
                            ▼
                    ┌───────────────┐
                    │   PDF Loader  │
                    │    pypdf      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Chunker     │
                    │ 800 chars     │
                    │ 150 overlap   │
                    └───────┬───────┘
                            │
                            ▼
                ┌────────────────────────┐
                │ Sentence Transformers  │
                │  all-MiniLM-L6-v2      │
                └────────────┬───────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │    ChromaDB    │
                    │ Vector Store   │
                    └───────┬────────┘
                            │
                     Semantic Search
                            │
                            ▼
                    Relevant PDF Chunks
                            │
                            ▼
                   ┌─────────────────┐
                   │   Groq LLM      │
                   │  Llama Model    │
                   └────────┬────────┘
                            │
                            ▼
                    Grounded Response
                            │
                            ▼
                    Flask REST API
                            │
                            ▼
                    Streamlit Frontend
```

---

## RAG Pipeline

The core RAG pipeline follows these stages:

### 1. Document Loading

Government scheme PDFs are stored inside:

```text
data/pdfs/
```

The custom `PDFLoader` uses `pypdf.PdfReader` to extract text page by page.

Each extracted page is stored with metadata:

```python
{
    "text": "...",
    "metadata": {
        "source": "Sample_PM_KISAN_Knowledge_Base.pdf",
        "page": 1
    }
}
```

This allows the application to preserve the source document and page information throughout the retrieval pipeline.

---

### 2. Document Chunking

Large PDF pages are divided into smaller semantic chunks using a custom document chunker.

Current configuration:

```text
Chunk size   : 800 characters
Chunk overlap: 150 characters
```

The chunker attempts to split content around sentence boundaries and uses overlapping content to reduce loss of context between chunks.

---

### 3. Embedding Generation

Each chunk is converted into a numerical vector using:

```text
Sentence Transformers
all-MiniLM-L6-v2
```

The same embedding model is used during:

* document indexing
* user query processing

This allows the system to compare the semantic meaning of a user question with the semantic meaning of document chunks.

---

### 4. ChromaDB Vector Storage

The generated embeddings are stored in a persistent ChromaDB collection.

```text
data/chroma_store/
```

The project uses cosine similarity:

```python
metadata={"hnsw:space": "cosine"}
```

When a citizen asks a question, the question is embedded and compared against the stored document vectors.

The most relevant chunks are retrieved from ChromaDB.

---

### 5. Retrieval-Augmented Generation

The retrieved document chunks are combined with:

* retrieved context
* conversation history
* current citizen question

and passed to the Groq LLM through a grounded RAG prompt.

The model is explicitly instructed to answer only from the supplied government documents and avoid inventing information.

Conceptually:

```text
User Question
      │
      ▼
Query Embedding
      │
      ▼
ChromaDB Semantic Search
      │
      ▼
Relevant Document Chunks
      │
      ├──── Conversation History
      │
      ▼
RAG Prompt
      │
      ▼
Groq LLM
      │
      ▼
Grounded Answer
```

---

## Intent Classification

Before answering a question, the application uses a Groq-powered few-shot classifier to identify the user's intent.

Supported intents:

```text
ELIGIBILITY
DOCUMENTS
APPLICATION
BENEFITS
CSC_LOCATION
SCHEME_INFO
GENERAL_QUERY
```

The classifier also extracts useful slots such as:

```text
scheme
location
```

Example:

```text
Question:
"What documents do I need for Ayushman Bharat?"

Intent:
DOCUMENTS

Scheme:
ayushman bharat
```

The result is returned as structured JSON and safely parsed by the application.

---

## Eligibility Engine

Eligibility decisions are deliberately **not delegated to the LLM**.

The project uses deterministic Python rules for eligibility evaluation.

For example, the PM-KISAN eligibility service evaluates structured answers using predefined conditions.

The architecture is:

```text
Citizen Answers
      │
      ▼
Rule-Based Eligibility Engine
      │
      ▼
Eligible / Not Eligible
      │
      ▼
Optional Groq Explanation
```

This separation prevents the LLM from directly deciding a citizen's eligibility.

The LLM is used only to convert the already-determined result into an easier-to-understand explanation.

---

## CSC Centre Locator

The application also supports Common Service Centre lookup.

CSC data is stored in:

```text
app/database/csc_centers.json
```

When a user asks for a CSC centre, the system:

1. Identifies the `CSC_LOCATION` intent.
2. Extracts the city.
3. Searches the local JSON database.
4. Returns the matching CSC information.

The lookup is therefore handled separately from the RAG pipeline.

---

## Conversation Memory

The chatbot maintains lightweight session-based conversation history.

The implementation uses Python's:

```python
collections.deque
```

Each session stores the most recent conversation turns.

This allows follow-up questions to use recent conversational context without introducing a large external memory system.

---

## Technology Stack

| Component             | Technology                                 |
| --------------------- | ------------------------------------------ |
| Programming Language  | Python                                     |
| LLM                   | Groq                                       |
| LLM Model             | Configurable through environment variables |
| RAG                   | Custom RAG pipeline                        |
| Embeddings            | Sentence Transformers                      |
| Embedding Model       | `all-MiniLM-L6-v2`                         |
| Vector Database       | ChromaDB                                   |
| PDF Processing        | pypdf                                      |
| Backend               | Flask                                      |
| Frontend              | Streamlit                                  |
| API Communication     | REST / JSON                                |
| Configuration         | python-dotenv                              |
| Database for CSC Data | JSON                                       |
| Server                | Gunicorn compatible                        |

---

## Project Structure

```text
GovAssist-AI/
│
├── .env.example
├── .gitignore
├── config.py
├── requirements.txt
├── run.py
├── README.md
│
├── app/
│   │
│   ├── api/
│   │   ├── controller.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── __init__.py
│   │
│   ├── chatbot/
│   │   ├── intent_llm.py
│   │   ├── memory.py
│   │   ├── prompts.py
│   │   ├── rag.py
│   │   └── __init__.py
│   │
│   ├── database/
│   │   └── csc_centers.json
│   │
│   ├── embeddings/
│   │   ├── build_index.py
│   │   ├── embedding_model.py
│   │   ├── vector_store.py
│   │   └── __init__.py
│   │
│   ├── loaders/
│   │   ├── chunker.py
│   │   ├── json_loader.py
│   │   ├── pdf_loader.py
│   │   └── __init__.py
│   │
│   ├── models/
│   │   ├── groq_client.py
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── csc_locator.py
│   │   ├── eligibility_service.py
│   │   ├── scheme_service.py
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── data/
│   ├── pdfs/
│   │   ├── Sample_Ayushman_Bharat_Knowledge_Base.pdf
│   │   └── Sample_PM_KISAN_Knowledge_Base.pdf
│   │
│   └── chroma_store/
│
├── docs/
│   └── api_documentation.md
│
└── frontend/
    └── streamlit_app.py
```

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Hariprakash-23/GovAssist-AI.git
cd GovAssist-AI
```

Replace the repository URL if you choose a different GitHub repository name.

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file from the provided example:

```bash
copy .env.example .env
```

Add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
```

Optional configuration:

```env
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_DB_PATH=data/chroma_store
CHROMA_COLLECTION=gov_schemes
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

**Never commit `.env` to GitHub.**

The project is designed to load the API key from environment variables rather than hardcoding credentials in source code.

---

# Build the Vector Index

Before running the chatbot, build the ChromaDB index from the government PDFs:

```bash
python -m app.embeddings.build_index
```

The indexing pipeline is:

```text
PDF files
   ↓
PDFLoader
   ↓
DocumentChunker
   ↓
SentenceTransformer
   ↓
ChromaDB
```

The command recreates the configured ChromaDB collection and indexes the available PDF documents.

Whenever you add or modify PDFs inside:

```text
data/pdfs/
```

run the indexing command again.

---

# Run the Application

## Start the Flask API

```bash
python run.py
```

The API will start on:

```text
http://127.0.0.1:5000
```

---

## Start the Streamlit Frontend

Open another terminal:

```bash
streamlit run frontend/streamlit_app.py
```

The Streamlit application provides the citizen-facing conversational interface.

---

# API

The primary endpoint is:

```text
POST /chat
```

### Request

```json
{
    "question": "What is PM-KISAN?"
}
```

A session ID can also be supplied:

```json
{
    "question": "What documents are required?",
    "session_id": "user-123"
}
```

### Response

```json
{
    "success": true,
    "intent": "SCHEME_INFO",
    "answer": "....",
    "scheme": "pm kisan",
    "location": null
}
```

---

# Example Questions

The chatbot can handle questions such as:

```text
What is PM-KISAN?

Tell me about Ayushman Bharat.

What documents are required for this scheme?

How can I apply for PM-KISAN?

What benefits does PM-KISAN provide?

Am I eligible for PM-KISAN?

Where is the CSC centre in Chennai?
```

For questions covered by the indexed documents, the RAG pipeline retrieves relevant PDF content before generating the answer.

---

# Key Design Decisions

## 1. Custom PDF Processing

Instead of relying on a high-level document loader, the project directly uses:

```python
pypdf.PdfReader
```

This provides control over:

* page-level extraction
* document metadata
* chunk creation
* preprocessing

---

## 2. Custom Chunking

A lightweight sentence-aware chunker was implemented instead of relying on a framework-specific text splitter.

This keeps the retrieval pipeline transparent and allows chunk size and overlap to be configured directly.

---

## 3. Explicit Embedding Pipeline

Sentence Transformers are called directly during:

```text
Indexing
```

and:

```text
Query processing
```

This makes the semantic retrieval process explicit rather than hiding it behind a framework abstraction.

---

## 4. Persistent ChromaDB

ChromaDB provides persistent vector storage so that document embeddings do not need to be regenerated for every application request.

---

## 5. Grounded Generation

The RAG prompt instructs the LLM to answer only using retrieved government document context.

If relevant information cannot be found, the system is instructed to state that the information is unavailable rather than fabricate an answer.

---

## 6. Deterministic Eligibility

Eligibility decisions are separated from generative AI.

```text
Rules → Decision
LLM   → Explanation
```

This provides a more controlled architecture for rule-based government eligibility checks.

---

# GenAI Concepts Demonstrated

This project demonstrates several practical Generative AI concepts:

### Retrieval-Augmented Generation

Combines external knowledge retrieval with LLM generation.

### Semantic Search

Uses vector embeddings rather than simple keyword matching.

### Sentence Embeddings

Converts documents and queries into numerical representations for similarity comparison.

### Prompt Engineering

Uses structured prompts for:

* RAG response generation
* few-shot intent classification
* eligibility explanations

### Few-Shot Learning

The intent classifier receives examples of expected inputs and structured outputs.

### Conversational AI

Session-based conversation memory enables contextual follow-up questions.

### LLM Integration

Groq provides the inference layer for the generative and classification components.
