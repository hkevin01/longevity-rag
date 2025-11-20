"""FAISS-backed vector store wrapper with simple persistence.

This module attempts to use faiss if available. If not, it falls back to a
numpy-based brute-force index to allow the MVP to run in constrained
environments.

REQ-001: Vector store must support both FAISS and numpy fallback
REQ-002: Vector store must persist to disk with integrity validation
REQ-003: Search must validate inputs and handle edge cases
"""

from __future__ import annotations

import numpy as np
from pathlib import Path
from typing import Tuple, List
import logging

from src.utils.errors import (
    InvalidShapeError,
    EmptyInputError,
    PersistenceError,
    InvalidParameterError,
)
from src.utils.validation import (
    validate_2d_array,
    validate_k_value,
    validate_not_none,
)

logger = logging.getLogger(__name__)

try:
    import faiss
    _FAISS_AVAILABLE = True
except Exception:
    _FAISS_AVAILABLE = False


class FaissVectorStore:
    """Simple wrapper exposing load, search for embeddings.

    Data contract: index positions correspond to metadata lines stored in
    `data/processed/metadata.jsonl`.

    REQ-001: Validate embeddings shape and contents on initialization
    REQ-002: Support both FAISS and numpy fallback modes
    REQ-003: Normalize embeddings for cosine similarity

    Attributes:
        embeddings: 2D numpy array of shape (n_vectors, dimension)
        index: FAISS index (if available) or None
        _using_faiss: Boolean indicating if FAISS is being used
    """

    def __init__(self, embeddings: np.ndarray):
        """Initialize vector store with embeddings.

        Args:
            embeddings: 2D numpy array of shape (n_vectors, dimension)

        Raises:
            InvalidShapeError: If embeddings is not 2D array
            EmptyInputError: If embeddings is empty

        Time complexity: O(n*d) where n=num vectors, d=dimension
        Memory: O(n*d) for storing embeddings
        """
        # REQ-001: Validate embeddings shape
        validate_2d_array(embeddings, "embeddings")

        # Validate dimension > 0
        if embeddings.shape[1] == 0:
            raise InvalidShapeError(
                "embeddings dimension must be > 0",
                details={"shape": embeddings.shape}
            )

        self.embeddings = embeddings.astype(np.float32)
        self.index = None
        self._using_faiss = False

        if _FAISS_AVAILABLE:
            try:
                d = self.embeddings.shape[1]
                self.index = faiss.IndexFlatIP(d)
                faiss.normalize_L2(self.embeddings)
                self.index.add(self.embeddings)
                self._using_faiss = True
                logger.info(f"FAISS index created: {self.embeddings.shape[0]} vectors, dim={d}")
            except Exception as e:
                logger.warning(f"FAISS initialization failed: {e}. Falling back to numpy.")
                self._using_faiss = False

        if not self._using_faiss:
            # Keep embeddings normalized for cosine similarity
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self.embeddings = self.embeddings / norms
            logger.info(f"Numpy fallback index created: {self.embeddings.shape[0]} vectors, dim={embeddings.shape[1]}")

    @classmethod
    def build(cls, embeddings: np.ndarray) -> "FaissVectorStore":
        return cls(embeddings)

    def search(self, query_embedding: np.ndarray, k: int = 20) -> Tuple[List[int], List[float]]:
        """Search for top-k nearest neighbors.

        Args:
            query_embedding: 1D numpy array of same dimension as stored embeddings
            k: Number of nearest neighbors to return (default: 20)

        Returns:
            Tuple of (indices, scores) where:
                - indices: List of k indices into the embeddings array
                - scores: List of k similarity scores (higher = more similar)

        Raises:
            EmptyInputError: If query_embedding is None
            InvalidParameterError: If k is invalid or exceeds index size
            InvalidShapeError: If query_embedding has wrong dimension

        Time complexity: O(n*d) for numpy fallback, O(d) for FAISS
        Memory: O(k)
        """
        # REQ-003: Validate inputs
        validate_not_none(query_embedding, "query_embedding")

        # Convert to numpy array and validate
        q = np.array(query_embedding, dtype=np.float32)

        # Validate dimension matches
        expected_dim = self.embeddings.shape[1]
        if q.ndim == 1:
            actual_dim = q.shape[0]
        elif q.ndim == 2 and q.shape[0] == 1:
            q = q.flatten()
            actual_dim = q.shape[0]
        else:
            raise InvalidShapeError(
                "query_embedding must be 1D array or 2D array with shape (1, d)",
                details={"shape": q.shape}
            )

        if actual_dim != expected_dim:
            raise InvalidShapeError(
                "query_embedding dimension mismatch",
                details={
                    "query_dim": actual_dim,
                    "index_dim": expected_dim
                }
            )

        # Validate k
        max_k = len(self.embeddings)
        validate_k_value(k, "k", max_k=max_k)

        # Adjust k if it exceeds available vectors
        k = min(k, max_k)

        if self._using_faiss and self.index is not None:
            try:
                faiss.normalize_L2(q.reshape(1, -1))
                D, I = self.index.search(q.reshape(1, -1), k)
                return I[0].tolist(), D[0].tolist()
            except Exception as e:
                logger.error(f"FAISS search failed: {e}. Falling back to numpy.")
                # Fall through to numpy implementation

        # Numpy fallback: cosine similarity by dot product with normalized embeddings
        norm = np.linalg.norm(q)
        if norm < 1e-12:
            logger.warning("query_embedding is zero vector, returning zero similarities")
            return list(range(k)), [0.0] * k

        q = q / norm
        sims = self.embeddings.dot(q)
        idx = np.argsort(-sims)[:k]
        return idx.tolist(), sims[idx].tolist()

    def save(self, path: str) -> None:
        """Save vector store to disk.

        Args:
            path: File path (will add .npz extension if not present)

        Raises:
            PersistenceError: If save fails

        Time complexity: O(n*d)
        Memory: O(n*d) during compression
        """
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)

            # Ensure .npz extension for numpy savez_compressed
            out_path = str(p)
            if not out_path.endswith(".npz"):
                out_path = out_path + ".npz"

            # Save with metadata
            np.savez_compressed(
                out_path,
                embeddings=self.embeddings,
                version="1.0",  # Format version for future compatibility
                using_faiss=self._using_faiss
            )

            # Verify save succeeded
            if not Path(out_path).exists():
                raise PersistenceError(
                    "Save operation appeared to succeed but file not found",
                    details={"path": out_path}
                )

            file_size = Path(out_path).stat().st_size
            if file_size == 0:
                raise PersistenceError(
                    "Saved file is empty",
                    details={"path": out_path}
                )

            logger.info(f"Vector store saved: {out_path} ({file_size} bytes)")

        except Exception as e:
            if isinstance(e, PersistenceError):
                raise
            raise PersistenceError(
                f"Failed to save vector store: {e}",
                details={"path": path, "error": str(e)}
            )

    @classmethod
    def load(cls, path: str) -> "FaissVectorStore":
        """Load vector store from disk.

        Args:
            path: File path (with or without .npz extension)

        Returns:
            FaissVectorStore instance

        Raises:
            PersistenceError: If load fails or data is corrupted

        Time complexity: O(n*d)
        Memory: O(n*d)
        """
        try:
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
                raise PersistenceError(
                    "Vector store file not found",
                    details={
                        "path": path,
                        "tried_paths": [str(p), str(p) + ".npz"]
                    }
                )

            # Load data
            data = np.load(str(candidate))

            # Validate required fields
            if "embeddings" not in data:
                raise PersistenceError(
                    "Corrupted vector store: missing 'embeddings' field",
                    details={"path": str(candidate)}
                )

            emb = data["embeddings"]

            # Validate loaded embeddings
            if emb.size == 0:
                raise PersistenceError(
                    "Corrupted vector store: empty embeddings",
                    details={"path": str(candidate)}
                )

            if emb.ndim != 2:
                raise PersistenceError(
                    "Corrupted vector store: invalid embeddings shape",
                    details={"path": str(candidate), "shape": emb.shape}
                )

            logger.info(f"Vector store loaded: {candidate} ({emb.shape[0]} vectors, dim={emb.shape[1]})")

            return cls.build(emb)

        except Exception as e:
            if isinstance(e, PersistenceError):
                raise
            raise PersistenceError(
                f"Failed to load vector store: {e}",
                details={"path": path, "error": str(e)}
            )

