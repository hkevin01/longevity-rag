"""FAISS-backed vector store wrapper with simple persistence.

This module attempts to use faiss if available. If not, it falls back to a
numpy-based brute-force index to allow the MVP to run in constrained
environments.
"""

from __future__ import annotations

import numpy as np
from pathlib import Path
from typing import Tuple, List

try:
    import faiss
    _FAISS_AVAILABLE = True
except Exception:
    _FAISS_AVAILABLE = False


class FaissVectorStore:
    """Simple wrapper exposing load, search for embeddings.

    Data contract: index positions correspond to metadata lines stored in
    `data/processed/metadata.jsonl`.
    """

    def __init__(self, embeddings: np.ndarray):
        self.embeddings = embeddings.astype(np.float32)
        self.index = None

        if _FAISS_AVAILABLE:
            d = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(d)
            faiss.normalize_L2(self.embeddings)
            self.index.add(self.embeddings)
        else:
            # Keep embeddings normalized for cosine similarity
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self.embeddings = self.embeddings / norms

    @classmethod
    def build(cls, embeddings: np.ndarray) -> "FaissVectorStore":
        return cls(embeddings)

    def search(self, query_embedding: np.ndarray, k: int = 20) -> Tuple[List[int], List[float]]:
        q = np.array(query_embedding, dtype=np.float32)
        if _FAISS_AVAILABLE and self.index is not None:
            faiss.normalize_L2(q.reshape(1, -1))
            D, I = self.index.search(q.reshape(1, -1), k)
            return I[0].tolist(), D[0].tolist()
        else:
            # cosine similarity by dot product with normalized embeddings
            q = q / (np.linalg.norm(q) + 1e-12)
            sims = self.embeddings.dot(q)
            idx = np.argsort(-sims)[:k]
            return idx.tolist(), sims[idx].tolist()

    def save(self, path: str) -> None:
        # Simple persistence: store as numpy .npz
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        # Ensure .npz extension for numpy savez_compressed
        out_path = str(p)
        if not out_path.endswith(".npz"):
            out_path = out_path + ".npz"
        np.savez_compressed(out_path, embeddings=self.embeddings)

    @classmethod
    def load(cls, path: str) -> "FaissVectorStore":
        p = Path(path)
        # Accept either exact path or path + .npz
        candidate = None
        if p.exists():
            candidate = p
        elif p.with_suffix(p.suffix + ".npz").exists():
            candidate = p.with_suffix(p.suffix + ".npz")
        elif Path(str(p) + ".npz").exists():
            candidate = Path(str(p) + ".npz")
        else:
            raise FileNotFoundError(path)

        data = np.load(str(candidate))
        emb = data["embeddings"]
        return cls.build(emb)

