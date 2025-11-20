"""Minimal RAG core for the longevity-rag MVP vertical slice.

Provides a LongevityRAG class that wires embeddings, vector store and a simple
generator together. This is intentionally small and resilient: if a FAISS index
is not present the class will raise a clear error instructing the user to run
the ingestion script.

Usage:
    from src.rag.core import LongevityRAG
    rag = LongevityRAG(index_path="data/embeddings/faiss_index.bin",
                       metadata_path="data/processed/metadata.jsonl")
    resp = rag.query("What are the effects of rapamycin on lifespan?")

"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.rag.vector_store import FaissVectorStore
from src.nlp.embeddings import Embeddings
from src.rag.generator import LLMGenerator


class LongevityRAG:
    """Thin RAG pipeline for MVP.

    - Loads a vector store (FAISS preferred, numpy fallback)
    - Uses an embeddings interface (PubMedBERT or mock)
    - Searches top-k chunks and returns text + citations
    """

    def __init__(
        self,
        index_path: str = "data/embeddings/faiss_index.bin",
        metadata_path: str = "data/processed/metadata.jsonl",
        embedder: Optional[Embeddings] = None,
        generator: Optional[LLMGenerator] = None,
    ) -> None:
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        self.embedder = embedder or Embeddings()
        self.generator = generator or LLMGenerator()

        # Resolve index path (accept with or without .npz)
        index_candidate = None
        if self.index_path.exists():
            index_candidate = self.index_path
        elif self.index_path.with_suffix(self.index_path.suffix + ".npz").exists():
            index_candidate = self.index_path.with_suffix(self.index_path.suffix + ".npz")
        elif Path(str(self.index_path) + ".npz").exists():
            index_candidate = Path(str(self.index_path) + ".npz")

        if index_candidate is None:
            raise FileNotFoundError(
                f"No index found at {self.index_path}. Please run scripts/ingest_sample.py first."
            )

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"No metadata found at {self.metadata_path}. Please run scripts/ingest_sample.py first."
            )

        self.store = FaissVectorStore.load(str(index_candidate))

        # Load metadata list (one JSON per line)
        self.metadata = []
        with self.metadata_path.open("r", encoding="utf8") as fh:
            for line in fh:
                try:
                    self.metadata.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    def query(self, question: str, k: int = 20) -> Dict[str, Any]:
        """Run a simple RAG query: embed, search, assemble, and generate.

        Returns a dict with keys: text, citations (list of pmids), confidence
        """
        q_emb = self.embedder.encode([question])[0]
        ids, scores = self.store.search(q_emb, k=k)

        # ids -> metadata mapping
        chunks = []
        pmids = []
        for idx, score in zip(ids, scores):
            if idx < 0 or idx >= len(self.metadata):
                continue
            md = self.metadata[idx]
            chunks.append({"score": float(score), "text": md.get("chunk_text", ""), "pmid": md.get("pmid")})
            if md.get("pmid"):
                pmids.append(md.get("pmid"))

        # Simple assembly: join top chunks
        assembled = "\n\n".join([c["text"] for c in chunks[:10]])

        # Call generator (mock) to produce answer; include citations
        prompt = f"Question: {question}\n\nContext:\n{assembled}\n"
        answer = self.generator.generate(prompt)

        # Confidence heuristic: average similarity of returned scores
        confidence = float(sum(scores) / len(scores)) if len(scores) > 0 else 0.0

        return {"text": answer, "citations": list(dict.fromkeys(pmids)), "confidence": confidence}

