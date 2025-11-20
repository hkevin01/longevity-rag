"""Minimal RAG core for the longevity-rag MVP vertical slice.

Provides a LongevityRAG class that wires embeddings, vector store and a simple
generator together. This is intentionally small and resilient: if a FAISS index
is not present the class will raise a clear error instructing the user to run
the ingestion script.

REQ-004: RAG pipeline must validate all inputs
REQ-005: RAG pipeline must handle missing files gracefully
REQ-006: RAG pipeline must log query metrics

Usage:
    # With default settings (tries real embeddings, falls back to mock)
    from src.rag.core import LongevityRAG
    rag = LongevityRAG()
    resp = rag.query("What are the effects of rapamycin on lifespan?")

    # Force mock embeddings (useful for testing)
    from src.nlp.embeddings import Embeddings
    rag = LongevityRAG(embedder=Embeddings(use_mock=True))

    # Use custom paths
    rag = LongevityRAG(
        index_path="data/embeddings/faiss_index",
        metadata_path="data/processed/metadata.jsonl"
    )

"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import time

from src.rag.vector_store import FaissVectorStore
from src.nlp.embeddings import Embeddings
from src.rag.generator import LLMGenerator
from src.utils.errors import (
    IndexNotFoundError,
    MetadataNotFoundError,
    CorruptedDataError,
    QueryError,
)
from src.utils.validation import (
    validate_not_empty,
    validate_k_value,
    validate_max_length,
)

logger = logging.getLogger(__name__)


class LongevityRAG:
    """Thin RAG pipeline for MVP.

    - Loads a vector store (FAISS preferred, numpy fallback)
    - Uses an embeddings interface (PubMedBERT or mock)
    - Searches top-k chunks and returns text + citations

    REQ-004: Validate all inputs and configurations
    REQ-005: Provide clear error messages for missing files
    REQ-006: Log metrics for observability

    Attributes:
        index_path: Path to FAISS/numpy index file
        metadata_path: Path to JSONL metadata file
        embedder: Embeddings instance for query encoding
        generator: LLMGenerator instance for answer generation
        store: FaissVectorStore instance
        metadata: List of metadata dicts
    """

    def __init__(
        self,
        index_path: str = "data/embeddings/faiss_index",
        metadata_path: str = "data/processed/metadata.jsonl",
        embedder: Optional[Embeddings] = None,
        generator: Optional[LLMGenerator] = None,
        use_mock_embeddings: bool = False,
        max_context_chunks: int = 10,
    ) -> None:
        """Initialize RAG pipeline.

        Args:
            index_path: Path to vector index file
            metadata_path: Path to metadata JSONL file
            embedder: Optional Embeddings instance (creates default if None)
            generator: Optional LLMGenerator instance (creates default if None)
            use_mock_embeddings: Use mock embeddings if embedder is None
            max_context_chunks: Maximum chunks to include in LLM context (default: 10)

        Raises:
            IndexNotFoundError: If index file not found
            MetadataNotFoundError: If metadata file not found or empty
            CorruptedDataError: If metadata file is corrupted

        Time complexity: O(n*d) where n=num vectors, d=dimension
        Memory: O(n*d) for index + O(m) for metadata where m=num documents
        """
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.max_context_chunks = max_context_chunks

        # Initialize embedder (use provided, or create with mock flag)
        if embedder is not None:
            self.embedder = embedder
        else:
            self.embedder = Embeddings(use_mock=use_mock_embeddings)

        self.generator = generator or LLMGenerator()

        # REQ-005: Resolve index path (accept with or without .npz)
        index_candidate = None
        if self.index_path.exists():
            index_candidate = self.index_path
        elif self.index_path.with_suffix(self.index_path.suffix + ".npz").exists():
            index_candidate = self.index_path.with_suffix(self.index_path.suffix + ".npz")
        elif Path(str(self.index_path) + ".npz").exists():
            index_candidate = Path(str(self.index_path) + ".npz")

        if index_candidate is None:
            raise IndexNotFoundError(
                "Vector index not found",
                details={
                    "path": str(self.index_path),
                    "suggestion": "Run: python scripts/ingest_sample.py"
                }
            )

        if not self.metadata_path.exists():
            raise MetadataNotFoundError(
                "Metadata file not found",
                details={
                    "path": str(self.metadata_path),
                    "suggestion": "Run: python scripts/ingest_sample.py"
                }
            )

        # Load vector store
        logger.info(f"Loading vector store from {index_candidate}")
        self.store = FaissVectorStore.load(str(index_candidate))

        # Load metadata list (one JSON per line)
        logger.info(f"Loading metadata from {self.metadata_path}")
        self.metadata = []
        line_num = 0
        skipped_lines = 0

        with self.metadata_path.open("r", encoding="utf8") as fh:
            for line in fh:
                line_num += 1
                line = line.strip()
                if not line:
                    continue

                try:
                    self.metadata.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipped malformed JSON at line {line_num}: {e}")
                    skipped_lines += 1

        # Validate we loaded at least one metadata entry
        if len(self.metadata) == 0:
            raise MetadataNotFoundError(
                "Metadata file is empty or corrupted",
                details={
                    "path": str(self.metadata_path),
                    "lines_read": line_num,
                    "lines_skipped": skipped_lines
                }
            )

        if skipped_lines > 0:
            logger.warning(f"Loaded {len(self.metadata)} metadata entries, skipped {skipped_lines} malformed lines")
        else:
            logger.info(f"Loaded {len(self.metadata)} metadata entries")

        logger.info("LongevityRAG initialized successfully")

    def query(self, question: str, k: int = 20) -> Dict[str, Any]:
        """Run a simple RAG query: embed, search, assemble, and generate.

        Args:
            question: User's question (max 10,000 characters)
            k: Number of chunks to retrieve (default: 20)

        Returns:
            Dict with keys:
                - text: Generated answer string
                - citations: List of unique PMIDs
                - confidence: Float in [0, 1] indicating retrieval confidence
                - metadata: Dict with query metrics (time, chunks_used)

        Raises:
            EmptyInputError: If question is empty
            InputTooLargeError: If question exceeds 10,000 characters
            InvalidParameterError: If k is invalid
            QueryError: If query execution fails

        Time complexity: O(n*d + k*log(n)) where n=index size, d=dimension, k=top_k
        Memory: O(k) for retrieved chunks
        """
        # REQ-004: Validate inputs
        start_time = time.time()

        try:
            validate_not_empty(question, "question")
            validate_max_length(question, "question", max_length=10000)
            validate_k_value(k, "k")  # Just validate k > 0, don't enforce max

            # Auto-cap k to available documents
            if k > len(self.metadata):
                logger.warning(f"k={k} exceeds available documents ({len(self.metadata)}), capping to {len(self.metadata)}")
                k = len(self.metadata)

            logger.info(f"Query received: {question[:100]}..." if len(question) > 100 else f"Query received: {question}")

            # Step 1: Encode query
            encode_start = time.time()
            q_emb = self.embedder.encode([question])[0]
            encode_time = time.time() - encode_start
            logger.debug(f"Query encoding took {encode_time:.3f}s")

            # Step 2: Search vector store
            search_start = time.time()
            ids, scores = self.store.search(q_emb, k=k)
            search_time = time.time() - search_start
            logger.debug(f"Vector search took {search_time:.3f}s")

            # Step 3: Retrieve chunks and build context
            chunks = []
            pmids = []
            invalid_indices = 0

            for idx, score in zip(ids, scores):
                # REQ-004: Validate index bounds
                if idx < 0 or idx >= len(self.metadata):
                    logger.warning(f"Invalid index {idx} returned from search (valid range: [0, {len(self.metadata)}))")
                    invalid_indices += 1
                    continue

                md = self.metadata[idx]
                chunk_text = md.get("chunk_text", "")
                pmid = md.get("pmid")

                chunks.append({
                    "score": float(score),
                    "text": chunk_text,
                    "pmid": pmid
                })

                if pmid:
                    pmids.append(pmid)

            if invalid_indices > 0:
                logger.warning(f"Skipped {invalid_indices} invalid indices from search results")

            if len(chunks) == 0:
                logger.warning("No valid chunks retrieved")
                return {
                    "text": "No relevant information found.",
                    "citations": [],
                    "confidence": 0.0,
                    "metadata": {
                        "query_time_seconds": time.time() - start_time,
                        "chunks_retrieved": 0,
                        "chunks_used": 0
                    }
                }

            # Step 4: Assemble context (use top N chunks)
            context_chunks = chunks[:self.max_context_chunks]
            assembled = "\n\n".join([c["text"] for c in context_chunks])

            logger.debug(f"Using {len(context_chunks)} chunks for context")

            # Step 5: Generate answer
            generate_start = time.time()
            prompt = f"Question: {question}\n\nContext:\n{assembled}\n"
            answer = self.generator.generate(prompt)
            generate_time = time.time() - generate_start
            logger.debug(f"Answer generation took {generate_time:.3f}s")

            # Step 6: Calculate confidence
            # Confidence heuristic: average similarity of returned scores
            confidence = 0.0 if not scores else float(sum(scores) / len(scores))

            # Normalize confidence to [0, 1] range (cosine similarity is already in [-1, 1])
            confidence = max(0.0, min(1.0, (confidence + 1.0) / 2.0))

            total_time = time.time() - start_time

            # REQ-006: Log query metrics
            logger.info(
                f"Query completed in {total_time:.3f}s "
                f"(encode={encode_time:.3f}s, search={search_time:.3f}s, generate={generate_time:.3f}s) "
                f"| chunks={len(context_chunks)} | confidence={confidence:.3f}"
            )

            return {
                "text": answer,
                "citations": list(dict.fromkeys(pmids)),  # Deduplicate while preserving order
                "confidence": confidence,
                "metadata": {
                    "query_time_seconds": total_time,
                    "chunks_retrieved": len(chunks),
                    "chunks_used": len(context_chunks),
                    "encode_time_seconds": encode_time,
                    "search_time_seconds": search_time,
                    "generate_time_seconds": generate_time,
                }
            }

        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            if isinstance(e, (validate_not_empty, validate_max_length, validate_k_value).__class__):
                raise
            raise QueryError(
                f"Query execution failed: {e}",
                details={"question": question[:100], "error": str(e)}
            )

