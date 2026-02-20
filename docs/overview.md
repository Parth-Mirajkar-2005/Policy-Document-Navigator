# Overview

## Purpose
PolicyNavigator is an AI-powered tool that makes government policy documents accessible to everyone. Upload any policy PDF, get a plain-language summary, and ask questions about its contents using natural language.

## Key Features
- **PDF Upload**: Drag-and-drop PDF upload with automatic text extraction and chunking.
- **RAG Pipeline**: Retrieval-Augmented Generation — finds relevant sections using TF-IDF search, then generates answers using an LLM.
- **AI Summaries**: Plain-language summaries structured with purpose, key provisions, affected parties, and important details.
- **Chat Interface**: Ask natural language questions about uploaded documents and get cited answers.
- **Document Management**: Browse, summarize, query, and delete uploaded documents.
- **Dashboard**: Live stats showing documents processed, summaries generated, and chunks indexed.

## Benefits
- Makes complex government legislation understandable for regular citizens.
- No complex infrastructure required — runs locally with minimal dependencies.
- Fast and lightweight — pure Python search with LLM generation only when needed.

## Technologies
- **Backend**: Flask (Python)
- **Frontend**: Vanilla HTML, CSS, JavaScript
- **AI/LLM**: Groq API (Llama 3.3 70B)
- **Search**: TF-IDF keyword-based retrieval (pure Python)
- **PDF Processing**: pdfplumber
- **Storage**: JSON files (no database required)
