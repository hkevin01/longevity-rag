---
name: Cross-Encoder Reranking
about: Implement cross-encoder reranking for improved retrieval quality
title: '[FEATURE] Implement cross-encoder reranking'
labels: enhancement, phase-2, retrieval
assignees: ''
---

## Description
Implement cross-encoder reranking to improve retrieval quality by re-scoring candidate passages with a more powerful model.

## Current Status
⏳ **TODO** - No implementation exists yet

## Background
Bi-encoder retrieval (current PubMedBERT approach) is fast but less accurate. Cross-encoders jointly encode query + passage pairs for better relevance scoring, but are too slow for first-stage retrieval. The optimal strategy is:
1. **Bi-encoder**: Fast retrieval of top-100 candidates
2. **Cross-encoder**: Accurate reranking of top-100 → top-20

## Requirements

### Core Features
- [ ] Cross-encoder model loading (biomedical-specific)
- [ ] Batch reranking of candidate passages
- [ ] Confidence score calibration
- [ ] Two-stage retrieval pipeline (bi-encoder → cross-encoder)
- [ ] Configurable k1 (candidates) and k2 (final results)

### Model Options

**Primary Model:**
- `cross-encoder/ms-marco-MiniLM-L-6-v2` (Fast, general domain)
- 384MB, ~50ms per query-doc pair on CPU

**Biomedical Alternatives:**
- `pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb` (Clinical NLI)
- `naver/trecdl22-crossencoder-debertav3` (High accuracy, slower)
- Fine-tuned on PubMed QA datasets (future work)

### API Design
```python
from src.rag.reranker import CrossEncoderReranker

# Initialize reranker
reranker = CrossEncoderReranker(
    model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
    device="cuda"
)

# Two-stage retrieval
# Stage 1: Bi-encoder retrieves top-100
candidates = vector_store.search(query_embedding, k=100)

# Stage 2: Cross-encoder reranks to top-20
query = "What are the longevity benefits of rapamycin?"
passages = [chunks[idx] for idx in candidates]
reranked = reranker.rerank(query, passages, top_k=20)

# Returns: [
#   {"doc_id": 42, "text": "...", "score": 0.95, "rank": 1},
#   {"doc_id": 17, "text": "...", "score": 0.89, "rank": 2},
#   ...
# ]
```

### Integration with RAG Pipeline
```python
# Before (bi-encoder only)
contexts = vector_store.search(query_embedding, k=20)

# After (two-stage)
candidates = vector_store.search(query_embedding, k=100)  # Over-retrieve
passages = [chunks[idx] for idx in candidates]
reranked = reranker.rerank(query, passages, top_k=20)  # Precise rerank
contexts = reranked  # Use reranked results for LLM
```

### Performance Targets
- [ ] <500ms reranking latency for 100 candidates
- [ ] 15-30% improvement in recall@20 vs bi-encoder alone
- [ ] 10-20% improvement in NDCG@20
- [ ] Support batch reranking (parallel processing)

### Metrics
- [ ] Recall@K before/after reranking
- [ ] NDCG@K before/after reranking
- [ ] Reranking latency (p50, p95, p99)
- [ ] Score distribution analysis

## Testing Requirements
- [ ] Unit tests for reranking logic
- [ ] Benchmark tests on BEIR biomedical datasets
- [ ] A/B tests comparing bi-encoder vs two-stage
- [ ] Latency tests at different k1 values (50, 100, 200)
- [ ] Integration tests with full RAG pipeline

## Documentation
- [ ] Reranking architecture diagram
- [ ] Model selection guide (speed vs accuracy)
- [ ] Hyperparameter tuning guide (k1, k2)
- [ ] Performance benchmarks and ablation studies
- [ ] Fine-tuning guide for custom datasets

## Dependencies
- sentence-transformers>=2.2.0 (includes CrossEncoder)
- torch>=2.0.0

## Acceptance Criteria
- [ ] Cross-encoder reranker loads and runs inference
- [ ] Two-stage retrieval improves recall@20 by >15%
- [ ] Reranking latency <500ms for 100 candidates
- [ ] Integration with RAG pipeline complete
- [ ] All tests pass
- [ ] Documentation with ablation studies

## Related Issues
- Related to: PubMedBERT embeddings (✅ COMPLETE)
- Related to: Vector store optimization (#01)
- Complements: Redis caching (#04) for caching reranked results

## References
- Cross-Encoders for Reranking: https://www.sbert.net/examples/applications/cross-encoder/README.html
- MS MARCO Reranking: https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2
- BEIR Benchmark: https://github.com/beir-cellar/beir
- Pinecone Reranking Guide: https://www.pinecone.io/learn/series/rag/rerankers/
