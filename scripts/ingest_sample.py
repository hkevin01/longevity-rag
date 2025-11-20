"""Ingest a small sample of PubMed abstracts and build a FAISS index.

This script is intentionally minimal: it reads files from
`data/raw/sample_pubmed/`, extracts title+abstract, chunk them (512 tokens,
50 overlap using a simple whitespace tokenizer), encodes with the Embeddings
class, and saves per-chunk metadata to `data/processed/metadata.jsonl` and
persists embeddings to `data/embeddings/faiss_index.bin`.

Run:
    python scripts/ingest_sample.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from src.utils.pubmed_client import list_sample_files, parse_sample_file
from src.nlp.embeddings import Embeddings
from src.rag.vector_store import FaissVectorStore


CHUNK_TOKENS = 512
OVERLAP = 50


def simple_tokenize(text: str) -> List[str]:
    return text.split()


def detokenize(tokens: List[str]) -> str:
    return " ".join(tokens)


def chunk_text(text: str, chunk_tokens: int = CHUNK_TOKENS, overlap: int = OVERLAP):
    tokens = simple_tokenize(text)
    if not tokens:
        return []
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_tokens, len(tokens))
        chunk = detokenize(tokens[start:end])
        chunks.append(chunk)
        if end == len(tokens):
            break
        start = end - overlap
    return chunks


def main():
    data_dir = Path("data/raw/sample_pubmed")
    processed_dir = Path("data/processed")
    embed_dir = Path("data/embeddings")
    processed_dir.mkdir(parents=True, exist_ok=True)
    embed_dir.mkdir(parents=True, exist_ok=True)

    files = list_sample_files(str(data_dir))
    if not files:
        print("No sample files found in data/raw/sample_pubmed. Place JSON or text files there.")
        return

    metadata_path = processed_dir / "metadata.jsonl"
    embeddings = []

    emb = Embeddings()

    # Read existing metadata if any
    if metadata_path.exists():
        metadata_path.unlink()

    all_chunks = []

    for f in files:
        rec = parse_sample_file(f)
        text = (rec.get("title", "") or "") + "\n\n" + (rec.get("abstract", "") or "")
        chunks = chunk_text(text)
        for c in chunks:
            md = {"pmid": rec.get("pmid"), "chunk_text": c}
            all_chunks.append(md)

    # Encode in batches
    texts = [c["chunk_text"] for c in all_chunks]
    vectors = emb.encode(texts)

    # Save metadata
    with metadata_path.open("w", encoding="utf8") as fh:
        for md in all_chunks:
            fh.write(json.dumps(md, ensure_ascii=False) + "\n")

    import numpy as np

    mat = np.vstack(vectors).astype('float32')
    store = FaissVectorStore.build(mat)
    store.save(str(embed_dir / "faiss_index.bin"))

    print(f"Ingested {len(files)} files -> {len(all_chunks)} chunks. Index saved to {embed_dir}/faiss_index.bin")


if __name__ == "__main__":
    main()

