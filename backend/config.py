import os
from dotenv import load_dotenv

# Load .env from the project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
DOCS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documents.json')
