import json
from pathlib import Path

from src.rag.core import LongevityRAG


def test_rag_query_structure(tmp_path, monkeypatch):
    # Create tiny sample metadata and index
    md = [{"pmid": "PMID:1", "chunk_text": "This is evidence A."}, {"pmid": "PMID:2", "chunk_text": "This is evidence B."}]
    meta_file = tmp_path / "metadata.jsonl"
    with meta_file.open("w", encoding="utf8") as fh:
        for m in md:
            fh.write(json.dumps(m) + "\n")

    # Create embeddings for two dummy chunks
    import numpy as np
    emb = np.random.RandomState(0).randn(2, 768).astype('float32')
    from src.rag.vector_store import FaissVectorStore
    store = FaissVectorStore.build(emb)
    idx_path = tmp_path / "faiss_index"
    store.save(str(idx_path))

    # Monkeypatch paths
    rag = LongevityRAG(index_path=str(idx_path), metadata_path=str(meta_file))
    out = rag.query("What is rapamycin?")
    assert isinstance(out, dict)
    assert "text" in out and "citations" in out and "confidence" in out

