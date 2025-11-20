### API: /api/v1/query

POST /api/v1/query

Request JSON:

{
  "question": "Show me evidence for senolytic compounds in mouse models",
  "max_results": 10
}

Response JSON:

{
  "text": "... synthesized answer ...",
  "citations": ["PMID:33495399", "PMID:29989283"],
  "confidence": 0.92
}

Error example (index missing):

{
  "error": {
    "code": "INDEX_NOT_BUILT",
    "message": "No vector index found. Please run scripts/ingest_sample.py."
  }
}

