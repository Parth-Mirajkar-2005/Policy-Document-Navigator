# Installation and Setup

## Prerequisites
- Python 3.8+
- Git
- A free Groq API key (get one at https://console.groq.com/keys)

## Steps

### 1. Clone the repository
```bash
git clone https://github.com/Parth-Mirajkar-2005/Policy-Document-Navigator.git
cd Policy-Document-Navigator
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root and add your Groq API key:
```
GROQ_API_KEY=gsk_your_key_here
```

### 5. Run the app
```bash
python backend/app.py
```

Open **http://localhost:5000** in your browser.

## Dependencies
| Package | Purpose |
|---------|---------|
| Flask | Web server and API |
| Flask-CORS | Cross-origin support |
| pdfplumber | PDF text extraction |
| groq | Groq LLM API client |
| python-dotenv | Environment variable loading |
