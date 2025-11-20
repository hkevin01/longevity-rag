from src.rag.vector_store import FaissVectorStore
from src.nlp.embeddings import Embeddings
from scripts.ingest_sample import chunk_text
import numpy as np


def test_chunking_overlap():
    text = "".join([f"word{i} " for i in range(600)])
    chunks = chunk_text(text, chunk_tokens=100, overlap=10)
    # Ensure overlap
    assert len(chunks) >= 6
    # Ensure overlap size
    t0 = chunks[0].split()
    t1 = chunks[1].split()
    assert t0[-10:] == t1[:10]


def test_embeddings_dim():
    e = Embeddings()
    v = e.encode(["test"])[0]
    assert len(v) == 768

