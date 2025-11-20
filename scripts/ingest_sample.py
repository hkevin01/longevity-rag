"""Ingest a small sample of PubMed abstracts and build a FAISS index.

This script reads files from `data/raw/sample_pubmed/`, extracts title+abstract,
chunks them (512 tokens, 50 overlap using a simple whitespace tokenizer),
encodes with the Embeddings class (real PubMedBERT or mock), and saves
per-chunk metadata to `data/processed/metadata.jsonl` and persists embeddings
to `data/embeddings/faiss_index.bin`.

Usage:
    # Use real PubMedBERT embeddings (requires transformers + torch)
    python scripts/ingest_sample.py

    # Use mock embeddings (for testing without transformers)
    python scripts/ingest_sample.py --mock

    # Use GPU if available
    python scripts/ingest_sample.py --device cuda
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
    parser = argparse.ArgumentParser(description="Ingest sample PubMed data and build FAISS index")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock embeddings instead of real PubMedBERT"
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device for embeddings model (cpu/cuda/mps). Auto-detect if not specified."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for encoding (default: 32)"
    )
    args = parser.parse_args()

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

    # Initialize embeddings with user-specified mode
    print(f"Initializing embeddings (mock={args.mock}, device={args.device}, batch_size={args.batch_size})...")
    emb = Embeddings(
        use_mock=args.mock,
        device=args.device,
        batch_size=args.batch_size
    )
    print(f"Using: {emb}")

    # Read existing metadata if any
    if metadata_path.exists():
        metadata_path.unlink()

    all_chunks = []

    print(f"Processing {len(files)} files...")
    for i, f in enumerate(files, 1):
        rec = parse_sample_file(f)
        text = (rec.get("title", "") or "") + "\n\n" + (rec.get("abstract", "") or "")
        chunks = chunk_text(text)
        for c in chunks:
            md = {"pmid": rec.get("pmid"), "chunk_text": c}
            all_chunks.append(md)

        if i % 10 == 0 or i == len(files):
            print(f"  Processed {i}/{len(files)} files ({len(all_chunks)} chunks so far)...")

    # Encode in batches
    print(f"Encoding {len(all_chunks)} chunks with {emb}...")
    texts = [c["chunk_text"] for c in all_chunks]
    vectors = emb.encode(texts)
    print(f"  Encoding complete!")

    # Save metadata
    print(f"Saving metadata to {metadata_path}...")
    with metadata_path.open("w", encoding="utf8") as fh:
        for md in all_chunks:
            fh.write(json.dumps(md, ensure_ascii=False) + "\n")

    import numpy as np

    print(f"Building vector store...")
    mat = np.vstack(vectors).astype('float32')
    store = FaissVectorStore.build(mat)
    index_path = embed_dir / "faiss_index"
    store.save(str(index_path))

    print(f"\n✅ Success!")
    print(f"  Files ingested: {len(files)}")
    print(f"  Chunks created: {len(all_chunks)}")
    print(f"  Index saved to: {index_path}.npz")
    print(f"  Metadata saved to: {metadata_path}")
    print(f"\nTo query the system:")
    print(f"  from src.rag.core import LongevityRAG")
    print(f"  rag = LongevityRAG()")
    print(f"  response = rag.query('What are the effects of rapamycin?')")
    print(f"  print(response)")


if __name__ == "__main__":
    main()

