"""Tests for embeddings module."""

import pytest
from src.nlp.embeddings import Embeddings


def test_embeddings_mock_mode():
    """Test mock embeddings mode."""
    emb = Embeddings(use_mock=True)
    vectors = emb.encode(["test text 1", "test text 2"])
    
    assert len(vectors) == 2
    assert len(vectors[0]) == 768
    assert len(vectors[1]) == 768
    
    # Verify deterministic: same text = same embedding
    vectors2 = emb.encode(["test text 1"])
    assert vectors[0] == vectors2[0]


def test_embeddings_dimension():
    """Test embeddings have correct dimension."""
    emb = Embeddings(use_mock=True, dim=768)
    v = emb.encode(["test"])[0]
    assert len(v) == 768


def test_embeddings_normalization():
    """Test embeddings are normalized."""
    import numpy as np
    
    emb = Embeddings(use_mock=True)
    vectors = emb.encode(["test text"])
    
    # Check L2 norm is approximately 1.0
    norm = np.linalg.norm(vectors[0])
    assert abs(norm - 1.0) < 0.01


def test_embeddings_repr():
    """Test embeddings string representation."""
    emb_mock = Embeddings(use_mock=True)
    assert "mock" in str(emb_mock).lower()
    
    emb_real = Embeddings(use_mock=False)
    # Should show 'real' or 'mock' depending on transformers availability
    assert "mode=" in str(emb_real)


def test_embeddings_batch_encoding():
    """Test batch encoding works."""
    emb = Embeddings(use_mock=True)
    texts = [f"text {i}" for i in range(100)]
    vectors = emb.encode(texts)
    
    assert len(vectors) == 100
    assert all(len(v) == 768 for v in vectors)


@pytest.mark.skipif(
    True,  # Skip by default since it requires downloading model
    reason="Requires transformers + model download (440MB)"
)
def test_embeddings_real_mode():
    """Test real PubMedBERT embeddings (skipped by default)."""
    try:
        import transformers
        import torch
    except ImportError:
        pytest.skip("transformers or torch not installed")
    
    # This test is skipped by default to avoid long download
    emb = Embeddings(use_mock=False)
    vectors = emb.encode(["rapamycin extends lifespan"])
    
    assert len(vectors) == 1
    assert len(vectors[0]) == 768
    assert "real" in str(emb).lower()
