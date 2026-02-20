"""
RAG Pipeline — TF-IDF retrieval + Groq LLM for generation.
Uses keyword-based search (no embedding API needed). Groq is used only for answer generation and summaries.
Groq is free, extremely fast, and has very generous rate limits.
"""
import json
import os
import math
from collections import Counter
from groq import Groq
import config

# Initialize Groq client
client = Groq(api_key=config.GROQ_API_KEY)

# Model to use (Groq free tier models — all fast and reliable)
MODEL = "llama-3.3-70b-versatile"

# Path to the chunk store file
STORE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vector_store.json')


# ------- Store (JSON-based) -------

def load_store():
    """Load the chunk store from disk."""
    if os.path.exists(STORE_PATH):
        with open(STORE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_store(store):
    """Save the chunk store to disk."""
    with open(STORE_PATH, 'w', encoding='utf-8') as f:
        json.dump(store, f)


# ------- Document Storage -------

def add_document(doc_id, chunks):
    """Store document chunks in the JSON store."""
    store = load_store()
    store[doc_id] = chunks
    save_store(store)


def remove_document(doc_id):
    """Remove a document's chunks from the JSON store."""
    store = load_store()
    if doc_id in store:
        del store[doc_id]
        save_store(store)


# ------- TF-IDF Retrieval -------

def tokenize(text):
    """Simple tokenizer — lowercase and split on non-alpha characters."""
    words = []
    word = ""
    for ch in text.lower():
        if ch.isalnum():
            word += ch
        else:
            if word:
                words.append(word)
            word = ""
    if word:
        words.append(word)
    return words


def compute_score(query_tokens, chunk_tokens, df, total_docs):
    """Compute BM25-like relevance score between query and a chunk."""
    tf = Counter(chunk_tokens)
    chunk_len = len(chunk_tokens)
    if chunk_len == 0:
        return 0

    score = 0
    for token in query_tokens:
        if token in tf:
            term_freq = tf[token] / chunk_len
            idf = math.log((total_docs + 1) / (1 + df.get(token, 0)))
            score += term_freq * idf
    return score


def query_documents(question, doc_id=None, n_results=5):
    """Retrieve the most relevant chunks for a question using TF-IDF scoring."""
    store = load_store()
    if not store:
        return []

    query_tokens = tokenize(question)
    if not query_tokens:
        return []

    # Collect all chunks (optionally filtered by doc_id)
    all_chunks = []
    doc_ids = [doc_id] if doc_id else list(store.keys())
    for did in doc_ids:
        if did in store:
            for chunk in store[did]:
                all_chunks.append(chunk)

    if not all_chunks:
        return []

    # Compute document frequency for IDF
    tokenized_chunks = [tokenize(chunk) for chunk in all_chunks]
    df = Counter()
    for tokens in tokenized_chunks:
        for token in set(tokens):
            df[token] += 1

    # Score each chunk
    scored = []
    for chunk, tokens in zip(all_chunks, tokenized_chunks):
        score = compute_score(query_tokens, tokens, df, len(all_chunks))
        scored.append((score, chunk))

    # Sort by score (highest first) and return top n
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:n_results]]


# ------- Generation (Groq) -------

def call_llm(prompt):
    """Call Groq LLM for text generation."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048
    )
    return response.choices[0].message.content


def generate_answer(question, context_chunks):
    """Generate an answer using Groq with retrieved context (RAG)."""
    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are a helpful government policy analyst. Answer the user's question
based ONLY on the following context from policy documents. If the answer cannot
be found in the context, say "I couldn't find this information in the uploaded documents."

Keep your answer clear and in plain language so a regular citizen can understand.

Context:
{context}

Question: {question}

Answer:"""

    return call_llm(prompt)


def generate_summary(text):
    """Generate a plain-language summary of a policy document."""
    max_chars = 15000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Document truncated for summarization...]"

    prompt = f"""You are a government policy expert. Provide a clear, plain-language summary
of the following policy document. Structure your summary as:

1. **Purpose**: What is this policy about?
2. **Key Provisions**: What are the main rules or requirements?
3. **Who is Affected**: Who does this policy impact?
4. **Important Details**: Any deadlines, penalties, or notable points.

Write so a regular citizen can easily understand.

Document:
{text}

Summary:"""

    return call_llm(prompt)
