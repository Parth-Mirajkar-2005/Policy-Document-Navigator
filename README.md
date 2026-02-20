# Policy Document Navigator

An AI-powered government policy analysis tool that uses **RAG (Retrieval-Augmented Generation)** to help citizens understand complex regulatory documents.

## Features

- **📤 PDF Upload** — Upload policy documents for AI processing
- **📊 Dashboard** — Live stats (documents processed, summaries generated, chunks indexed)
- **📄 Document Library** — Browse, summarize, query, and delete uploaded documents
- **💬 Ask Questions** — Chat with an AI about policy contents (RAG-powered)
- **📝 Plain-Language Summaries** — AI-generated structured summaries
- **🗑️ Document Management** — Delete documents and all associated data

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript (vanilla — no frameworks)
- **AI/LLM**: Groq API (Llama 3.3 70B)
- **Search**: TF-IDF keyword retrieval (pure Python)
- **PDF Parsing**: pdfplumber
- **Storage**: JSON files (no database required)

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 2. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Set up your API key

Get a free Groq API key from: https://console.groq.com/keys

Create a `.env` file in the project root:
```
GROQ_API_KEY=gsk_your_key_here
```

### 4. Run the app

```bash
python backend/app.py
```

Open **http://localhost:5000** in your browser.

## How It Works

1. **Upload** a PDF policy document
2. Text is extracted, chunked, and stored in a local JSON file
3. **Ask questions** — your query is matched against relevant chunks using TF-IDF scoring
4. **Groq LLM** generates an answer grounded in the actual policy text
5. **View summaries** — AI creates plain-language summaries with purpose, key provisions, and impact

## Project Structure

```
├── backend/
│   ├── app.py              # Flask API server
│   ├── config.py           # Environment configuration
│   ├── ingestion.py        # PDF extraction and text chunking
│   ├── rag.py              # RAG pipeline (TF-IDF + Groq LLM)
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Single-page app (Dashboard, Documents, Chat)
│   ├── style.css           # Light theme with responsive design
│   └── script.js           # Vanilla JS — all UI logic
├── docs/                   # Documentation
├── .gitignore
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload a PDF document |
| `GET` | `/api/documents` | List all documents |
| `DELETE` | `/api/documents/<id>` | Delete a document |
| `POST` | `/api/query` | Ask a question (RAG) |
| `GET` | `/api/summary/<id>` | Get/generate summary |

## License

MIT