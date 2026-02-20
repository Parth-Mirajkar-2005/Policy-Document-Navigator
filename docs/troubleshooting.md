# Troubleshooting

## Common Issues

### "Connection error" on summary/chat
- **Cause**: Groq API key is missing or invalid.
- **Fix**: Check your `.env` file has `GROQ_API_KEY=gsk_...` (key must start with `gsk_`).

### "Rate limit exceeded"
- **Cause**: Free tier API quota temporarily exhausted.
- **Fix**: Wait 1–2 minutes and try again. Groq's free tier allows ~6,000 requests/day.

### "Could not extract text from this PDF"
- **Cause**: The PDF is image-based (scanned) rather than text-based.
- **Fix**: Use a text-based PDF. Scanned PDFs require OCR (not currently supported).

### App won't start / ModuleNotFoundError
- **Cause**: Dependencies not installed or wrong virtual environment.
- **Fix**: Activate your venv and run `pip install -r backend/requirements.txt`.

### Upload works but summary is slow
- **Cause**: Large PDFs send a lot of text to the LLM.
- **Fix**: This is normal for large documents (50+ pages). Summary text is capped at 15,000 characters.

### Port 5000 already in use
- **Cause**: Another app is using port 5000.
- **Fix**: Change the port in `backend/app.py` → `app.run(debug=True, port=5001)`.

## Reset Everything
To start fresh, delete the data files and restart:
```bash
del backend\vector_store.json
del backend\documents.json
```
