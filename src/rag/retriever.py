"""Retriever abstraction for the RAG MVP.

Currently thin wrapper around the FaissVectorStore but lays ground for
adding hybrid retrieval or KG-backed expansion later.
"""

from __future__ import annotations

from typing import List, Tuple
from src.rag.vector_store import FaissVectorStore


class Retriever:
    def __init__(self, store: FaissVectorStore):
        self.store = store

    def retrieve(self, query_embedding, k: int = 20) -> Tuple[List[int], List[float]]:
        return self.store.search(query_embedding, k=k)

