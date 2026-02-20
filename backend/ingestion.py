import pdfplumber


def extract_text_from_pdf(filepath):
    """Extract all text from a PDF file.

    Returns:
        tuple: (extracted_text, page_count)
    """
    text = ""
    page_count = 0
    with pdfplumber.open(filepath) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text, page_count


def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks for embedding.

    Args:
        text: The full document text.
        chunk_size: Max characters per chunk.
        overlap: Number of overlapping characters between chunks.

    Returns:
        list: List of text chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks
