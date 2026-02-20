"""
Flask API for the Policy Document Navigator.
Serves the frontend and provides API endpoints for upload, query, documents, and summary.
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import uuid
import logging
from datetime import datetime

import config
from ingestion import extract_text_from_pdf, chunk_text
from rag import add_document, remove_document, query_documents, generate_answer, generate_summary

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- App Setup ---
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

logger.info(f"Initializing app. Upload folder: {config.UPLOAD_FOLDER}")
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)


# --- Document metadata helpers ---

def load_documents():
    """Load document metadata from JSON file."""
    if os.path.exists(config.DOCS_JSON):
        with open(config.DOCS_JSON, 'r') as f:
            return json.load(f)
    return {}


def save_documents(docs):
    """Save document metadata to JSON file."""
    with open(config.DOCS_JSON, 'w') as f:
        json.dump(docs, f, indent=2)


# --- Error Handlers ---

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions and return JSON instead of HTML."""
    # Pass through HTTP errors
    if hasattr(e, 'code'):
        return jsonify({'error': str(e)}), e.code
    
    # Handle non-HTTP exceptions
    logger.exception(f"Unhandled exception: {str(e)}")
    return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# --- Routes ---

@app.route('/')
def index():
    """Serve the frontend."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health')
def health():
    """Check if the API is up and running."""
    key_found = bool(config.GROQ_API_KEY) and config.GROQ_API_KEY != 'your_groq_api_key_here'
    return jsonify({
        'status': 'healthy',
        'groq_configured': key_found,
        'message': 'API key found' if key_found else 'MISSING GROQ_API_KEY! Please add it to Render Environment variables.',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/upload', methods=['POST'])
def upload():
    """Upload a PDF, extract text, chunk it, embed, and store in ChromaDB."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400

    logger.info(f"Received upload request: {file.filename}")

    try:
        # Save the uploaded file
        doc_id = str(uuid.uuid4())[:8]
        filepath = os.path.join(config.UPLOAD_FOLDER, f"{doc_id}.pdf")
        logger.info(f"Saving file to {filepath}")
        file.save(filepath)

        # Extract text from PDF
        logger.info("Extracting text from PDF...")
        text, page_count = extract_text_from_pdf(filepath)
        logger.info(f"Extracted {len(text)} characters from {page_count} pages.")

        if not text.strip():
            logger.warning("Extraction returned empty text.")
            os.remove(filepath)
            return jsonify({'error': 'Could not extract text from this PDF (it might be scanned or empty)'}), 400

        # Chunk and store
        logger.info(f"Chunking text into chunks...")
        chunks = chunk_text(text)
        logger.info(f"Adding {len(chunks)} chunks to store for doc_id {doc_id}")
        add_document(doc_id, chunks)

        # Save metadata
        logger.info("Saving document metadata...")
        docs = load_documents()
        docs[doc_id] = {
            'id': doc_id,
            'title': file.filename.replace('.pdf', ''),
            'filename': file.filename,
            'pages': page_count,
            'chunks': len(chunks),
            'uploaded_at': datetime.now().isoformat(),
            'summary': None
        }
        save_documents(docs)
        logger.info("Upload and processing complete.")

        return jsonify({
            'id': doc_id,
            'title': docs[doc_id]['title'],
            'message': 'Document uploaded and processed successfully'
        })

    except Exception as e:
        logger.exception(f"Exception during upload processing: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all uploaded documents."""
    docs = load_documents()
    return jsonify(list(docs.values()))


@app.route('/api/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document and all its data."""
    docs = load_documents()
    if doc_id not in docs:
        return jsonify({'error': 'Document not found'}), 404

    try:
        # Remove the uploaded PDF
        filepath = os.path.join(config.UPLOAD_FOLDER, f"{doc_id}.pdf")
        if os.path.exists(filepath):
            os.remove(filepath)

        # Remove chunks from vector store
        remove_document(doc_id)

        # Remove from metadata
        del docs[doc_id]
        save_documents(docs)

        return jsonify({'message': 'Document deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/query', methods=['POST'])
def query():
    """Answer questions based on the document summary."""
    data = request.json
    if not data or 'question' not in data:
        return jsonify({'error': 'No question provided'}), 400

    question = data['question']
    doc_id = data.get('doc_id')  # Optional: scope to a specific document

    try:
        docs = load_documents()

        if not docs:
            return jsonify({
                'answer': 'No documents uploaded yet. Please upload a document first.',
                'sources': []
            })

        # Collect summaries to answer from
        summaries = []

        if doc_id:
            # Single document
            if doc_id not in docs:
                return jsonify({'error': 'Document not found'}), 404

            doc = docs[doc_id]
            summary = doc.get('summary')

            # Auto-generate summary if not available
            if not summary:
                filepath = os.path.join(config.UPLOAD_FOLDER, f"{doc_id}.pdf")
                text, _ = extract_text_from_pdf(filepath)
                summary = generate_summary(text)
                docs[doc_id]['summary'] = summary
                save_documents(docs)

            summaries.append(f"Document: {doc['title']}\n{summary}")
        else:
            # All documents
            for did, doc in docs.items():
                summary = doc.get('summary')
                if not summary:
                    filepath = os.path.join(config.UPLOAD_FOLDER, f"{did}.pdf")
                    text, _ = extract_text_from_pdf(filepath)
                    summary = generate_summary(text)
                    docs[did]['summary'] = summary
                    save_documents(docs)
                summaries.append(f"Document: {doc['title']}\n{summary}")

        combined = "\n\n---\n\n".join(summaries)
        answer = generate_answer(question, [combined])

        return jsonify({
            'answer': answer,
            'sources': []
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summary/<doc_id>', methods=['GET'])
def get_summary(doc_id):
    """Generate or return a cached plain-language summary for a document."""
    docs = load_documents()
    if doc_id not in docs:
        return jsonify({'error': 'Document not found'}), 404

    # Return cached summary if available
    if docs[doc_id].get('summary'):
        return jsonify({'summary': docs[doc_id]['summary']})

    try:
        filepath = os.path.join(config.UPLOAD_FOLDER, f"{doc_id}.pdf")
        text, _ = extract_text_from_pdf(filepath)

        summary = generate_summary(text)

        # Cache the summary
        docs[doc_id]['summary'] = summary
        save_documents(docs)

        return jsonify({'summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
