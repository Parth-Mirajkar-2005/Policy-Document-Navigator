# Architecture

## High-Level Flow

```
[PDF Upload] → [Text Extraction (pdfplumber)] → [Chunking] → [JSON Store]
                                                                    ↓
[User Question] → [TF-IDF Retrieval] → [Top Chunks] → [Groq LLM] → [Answer]
```

## Components

### Backend (`backend/`)
- **`app.py`** — Flask application with API endpoints and static file serving.
- **`config.py`** — Environment variable loading (Groq API key, file paths).
- **`ingestion.py`** — PDF text extraction (pdfplumber) and overlapping text chunking.
- **`rag.py`** — Core RAG pipeline: TF-IDF retrieval, Groq LLM generation, and summary generation.

### Frontend (`frontend/`)
- **`index.html`** — Single-page app with Dashboard, Documents, and Chat tabs.
- **`style.css`** — Light theme with responsive design, stat cards, and modal.
- **`script.js`** — Vanilla JavaScript for all UI logic, API calls, and DOM manipulation.

### Data Storage
- **`vector_store.json`** — Stores text chunks for all uploaded documents (keyed by document ID).
- **`documents.json`** — Document metadata (title, pages, chunks, upload date, cached summaries).
- **`uploads/`** — Uploaded PDF files (named by document ID).

## Design Decisions
- **No database** — JSON files keep the project simple and portable.
- **TF-IDF over embeddings** — Avoids extra API calls and model dependencies. Works offline for retrieval.
- **Groq over Gemini** — More generous free tier rate limits (~6,000 requests/day vs ~50).
- **No frameworks** — Pure HTML/CSS/JS frontend for zero build complexity.
