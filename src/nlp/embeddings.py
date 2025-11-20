"""Embeddings interface for the MVP.

This implements a minimal `Embeddings` class that exposes `encode(texts)`
returning 768-dim vectors. If transformers and a PubMedBERT model are
available they can be wired here; otherwise a deterministic random vector is
used for reproducibility in tests.
"""

from __future__ import annotations

from typing import List
import numpy as np


class Embeddings:
    def __init__(self, dim: int = 768, seed: int = 1234):
        self.dim = dim
        self.rng = np.random.RandomState(seed)

    def encode(self, texts: List[str]) -> List[List[float]]:
        # Deterministic pseudo-embeddings for MVP
        outs = []
        for t in texts:
            h = abs(hash(t)) % (10 ** 8)
            self.rng.seed(h)
            v = self.rng.randn(self.dim).astype(float)
            # normalize
            v = v / (np.linalg.norm(v) + 1e-12)
            outs.append(v.tolist())
        return outs

