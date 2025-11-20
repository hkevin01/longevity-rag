# Embeddings Setup Guide

The Longevity RAG system supports two modes for text embeddings:

1. **Real PubMedBERT embeddings** (recommended for production)
2. **Mock embeddings** (for testing and development without ML dependencies)

## Real PubMedBERT Embeddings

### Requirements

Install transformers and PyTorch:

```bash
pip install transformers torch
```

For GPU support (much faster):
```bash
# CUDA 11.8
pip install torch --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Model Details

- **Model**: `microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext`
- **Dimensions**: 768
- **Training data**: PubMed abstracts and full-text articles
- **Performance**: Superior semantic understanding of biomedical text
- **Download size**: ~440 MB
- **First run**: Model downloads automatically from Hugging Face

### Usage

#### Ingestion with Real Embeddings

```bash
# CPU (slower but no GPU required)
python scripts/ingest_sample.py

# GPU (much faster)
python scripts/ingest_sample.py --device cuda

# Specify batch size (higher = faster but more memory)
python scripts/ingest_sample.py --device cuda --batch-size 64
```

#### Querying with Real Embeddings

```python
from src.rag.core import LongevityRAG

# LongevityRAG automatically uses real embeddings if available
rag = LongevityRAG()
response = rag.query("What interventions extend lifespan in mice?")
```

### Performance

On a typical workstation:
- **CPU**: ~5-10 texts/second
- **GPU (CUDA)**: ~50-200 texts/second
- **Memory**: ~2GB GPU RAM for batch_size=32

For 10,000 papers (typical dataset):
- **CPU**: ~2-4 hours
- **GPU**: ~10-20 minutes

---

## Mock Embeddings

### When to Use

- Testing without ML dependencies
- CI/CD pipelines
- Development on resource-constrained machines
- Quick prototyping

### Usage

#### Ingestion with Mock Embeddings

```bash
python scripts/ingest_sample.py --mock
```

#### Querying with Mock Embeddings

```python
from src.rag.core import LongevityRAG

# Force mock embeddings
rag = LongevityRAG(use_mock_embeddings=True)
response = rag.query("Test query")
```

Or pass a custom embedder:

```python
from src.nlp.embeddings import Embeddings
from src.rag.core import LongevityRAG

embedder = Embeddings(use_mock=True)
rag = LongevityRAG(embedder=embedder)
```

### Limitations

- **No semantic understanding**: Mock embeddings are deterministic pseudo-random vectors
- **Retrieval quality**: Will not match semantically similar documents
- **For testing only**: Do not use in production

---

## Auto-Detection

The system automatically detects if transformers is installed:

1. If `transformers` + `torch` are available → **Real embeddings**
2. If not available → **Mock embeddings** (with warning)

To verify which mode is being used:

```python
from src.nlp.embeddings import Embeddings

emb = Embeddings()
print(emb)  # Shows: Embeddings(mode=real, dim=768) or Embeddings(mode=mock, dim=768)
```

---

## Troubleshooting

### "No module named 'transformers'"

Install with:
```bash
pip install transformers torch
```

### "CUDA out of memory"

Reduce batch size:
```bash
python scripts/ingest_sample.py --batch-size 8
```

Or use CPU:
```bash
python scripts/ingest_sample.py --device cpu
```

### Slow ingestion on CPU

This is normal. Options:
- Use a smaller dataset for testing
- Use mock embeddings for development
- Use GPU if available

### Model download fails

The model downloads from Hugging Face on first use. If behind a firewall:
1. Pre-download the model on another machine
2. Copy to `~/.cache/huggingface/hub/`
3. Or set `HF_DATASETS_OFFLINE=1` environment variable

---

## Advanced Configuration

### Custom Model

Use a different BERT model:

```python
from src.nlp.embeddings import Embeddings

# Use BioBERT instead
embedder = Embeddings(
    model_name="dmis-lab/biobert-v1.1",
    use_mock=False
)
```

### Mixed Precision (faster on GPU)

Coming soon - will add FP16 support for 2x speedup.

---

## Comparison: Real vs Mock

| Feature | Real PubMedBERT | Mock |
|---------|-----------------|------|
| **Semantic understanding** | ✅ Excellent | ❌ None |
| **Retrieval quality** | ✅ High | ❌ Random |
| **Setup** | Requires transformers + torch | ✅ No dependencies |
| **Speed (CPU)** | Slow (~5 texts/sec) | ✅ Fast (~10k texts/sec) |
| **Speed (GPU)** | ✅ Fast (~100 texts/sec) | N/A |
| **Memory** | ~2GB GPU / 4GB RAM | ✅ Minimal |
| **Use case** | Production | Testing only |

---

## Recommended Setup

**For development:**
```bash
# Quick iteration without waiting for embeddings
python scripts/ingest_sample.py --mock
```

**For production:**
```bash
# Install ML stack
pip install transformers torch

# Ingest with GPU
python scripts/ingest_sample.py --device cuda

# Or CPU if no GPU
python scripts/ingest_sample.py
```

**For CI/CD:**
```yaml
# In .github/workflows/test.yml
- name: Test with mock embeddings
  run: python scripts/ingest_sample.py --mock
```
