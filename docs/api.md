# API Reference

## Endpoints

### `POST /api/upload`
Upload a PDF document for processing.
- **Body**: `multipart/form-data` with a `file` field (PDF only).
- **Response**: `{ "id": "abc123", "title": "document_name", "message": "..." }`

### `GET /api/documents`
List all uploaded documents with metadata.
- **Response**: Array of `{ "id", "title", "filename", "pages", "chunks", "uploaded_at", "summary" }`

### `DELETE /api/documents/<doc_id>`
Delete a document and all its data (PDF, chunks, metadata).
- **Response**: `{ "message": "Document deleted successfully" }`

### `POST /api/query`
Ask a question using RAG (retrieves relevant chunks, generates an answer).
- **Body**: `{ "question": "string", "doc_id": "optional_string" }`
- **Response**: `{ "answer": "string", "sources": ["chunk1", "chunk2", ...] }`

### `GET /api/summary/<doc_id>`
Generate or retrieve a cached plain-language summary.
- **Response**: `{ "summary": "string" }`

## Authentication
- No authentication required (local development tool).
- Groq API key is stored server-side in `.env` and never exposed to the frontend.
