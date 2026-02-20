# User Guide

## Getting Started
1. Run the app: `python backend/app.py`
2. Open **http://localhost:5000** in your browser.

## Dashboard
The landing page shows live stats (documents processed, summaries generated, chunks indexed) and the upload area.

## Uploading Documents
1. Go to the **Dashboard** tab.
2. Drag and drop a PDF into the upload zone, or click to browse.
3. Wait for processing (text extraction + chunking). You'll see a success message when done.

## Viewing Documents
1. Go to the **Documents** tab.
2. All uploaded documents are listed with page count, chunk count, and upload date.
3. Use the buttons on each document:
   - **View Summary** — generates an AI plain-language summary.
   - **Ask Question** — jumps to Chat with that document pre-selected.
   - **Delete** — removes the document and all its data.

## Asking Questions (Chat)
1. Go to the **Ask Questions** tab.
2. Select a specific document from the dropdown, or leave it on "All Documents".
3. Type your question and press Enter or click Send.
4. The AI retrieves relevant sections from the document and generates an answer with source citations.

## Tips
- Shorter PDFs (10–30 pages) get faster summaries.
- Be specific with your questions for better answers.
- You can ask follow-up questions in the same chat session.
