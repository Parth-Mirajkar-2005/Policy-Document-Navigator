import os
from dotenv import load_dotenv

# Base directory = the backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env from the project root (one level up from backend/)
load_dotenv(os.path.join(BASE_DIR, '..', '.env'))

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DOCS_JSON = os.path.join(BASE_DIR, 'documents.json')

