"""Embeddings interface for real and mock PubMedBERT embeddings.

This module provides the `Embeddings` class with two modes:
1. Real mode: Uses Hugging Face transformers + PubMedBERT (microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext)
2. Mock mode: Deterministic pseudo-embeddings for testing when transformers is unavailable

The class auto-detects if transformers is installed and falls back gracefully.
You can force mock mode by setting use_mock=True.

Usage:
    # Real embeddings (if transformers available)
    emb = Embeddings(use_mock=False)
    vectors = emb.encode(["rapamycin extends lifespan", "metformin effects"])

    # Mock embeddings (for tests)
    emb = Embeddings(use_mock=True)
    vectors = emb.encode(["test text"])
"""

from __future__ import annotations

from typing import List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Try to import transformers
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    _TRANSFORMERS_AVAILABLE = True
except ImportError:
    _TRANSFORMERS_AVAILABLE = False
    logger.warning(
        "transformers not available. Install with: pip install transformers torch. "
        "Falling back to mock embeddings."
    )


class Embeddings:
    """Embeddings wrapper supporting real PubMedBERT or mock mode.

    Args:
        model_name: HuggingFace model name (default: PubMedBERT)
        use_mock: Force mock mode even if transformers is available
        device: torch device ('cpu', 'cuda', or None for auto)
        batch_size: Batch size for encoding (larger = faster but more memory)
        dim: Embedding dimension (768 for PubMedBERT, used in mock mode)
        seed: Random seed for mock mode
    """

    def __init__(
        self,
        model_name: str = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext",
        use_mock: bool = False,
        device: Optional[str] = None,
        batch_size: int = 32,
        dim: int = 768,
        seed: int = 1234,
    ):
        self.dim = dim
        self.batch_size = batch_size
        self.use_mock = use_mock or not _TRANSFORMERS_AVAILABLE

        if self.use_mock:
            logger.info("Using mock embeddings (deterministic pseudo-random vectors)")
            self.rng = np.random.RandomState(seed)
            self.model = None
            self.tokenizer = None
        else:
            logger.info(f"Loading real embeddings model: {model_name}")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModel.from_pretrained(model_name)

                # Set device
                if device is None:
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                self.device = torch.device(device)
                self.model.to(self.device)
                self.model.eval()

                logger.info(f"Model loaded on device: {self.device}")
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {e}. Falling back to mock.")
                self.use_mock = True
                self.rng = np.random.RandomState(seed)
                self.model = None
                self.tokenizer = None

    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to 768-dim embedding vectors.

        Args:
            texts: List of text strings to encode

        Returns:
            List of embedding vectors (each vector is a list of 768 floats)
        """
        if self.use_mock:
            return self._encode_mock(texts)
        else:
            return self._encode_real(texts)

    def _encode_mock(self, texts: List[str]) -> List[List[float]]:
        """Deterministic pseudo-embeddings for testing."""
        outs = []
        for t in texts:
            h = abs(hash(t)) % (10 ** 8)
            self.rng.seed(h)
            v = self.rng.randn(self.dim).astype(float)
            # normalize
            v = v / (np.linalg.norm(v) + 1e-12)
            outs.append(v.tolist())
        return outs

    def _encode_real(self, texts: List[str]) -> List[List[float]]:
        """Real PubMedBERT embeddings using transformers."""
        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]

            # Tokenize
            encoded = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )

            # Move to device
            encoded = {k: v.to(self.device) for k, v in encoded.items()}

            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**encoded)
                # Use [CLS] token embedding (first token)
                embeddings = outputs.last_hidden_state[:, 0, :]

                # Normalize embeddings
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

                # Move to CPU and convert to list
                embeddings = embeddings.cpu().numpy()
                all_embeddings.extend(embeddings.tolist())

        return all_embeddings

    def __repr__(self):
        mode = "mock" if self.use_mock else "real"
        return f"Embeddings(mode={mode}, dim={self.dim})"

