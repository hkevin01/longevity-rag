---
name: Redis Caching Layer
about: Implement Redis caching for query results and embeddings
title: '[FEATURE] Implement Redis caching'
labels: enhancement, phase-3, performance
assignees: ''
---

## Description
Implement Redis caching layer to cache query embeddings, search results, and LLM responses for improved latency and cost reduction.

## Current Status
⏳ **TODO** - No implementation exists yet

## Requirements

### Core Features
- [ ] Redis connection management with connection pooling
- [ ] Query embedding cache (avoid re-encoding identical queries)
- [ ] Search results cache (cache top-k retrieval results)
- [ ] LLM response cache (cache generated answers)
- [ ] TTL (time-to-live) configuration per cache type
- [ ] Cache invalidation on index updates
- [ ] Cache hit/miss metrics

### Cache Types

#### 1. Query Embedding Cache
```python
# Cache key: hash of query text
# Value: embedding vector (768-dim array)
# TTL: 24 hours (query semantics rarely change)
cache_key = f"emb:{hash(query_text)}"
```

#### 2. Search Results Cache
```python
# Cache key: hash of query embedding + k + filters
# Value: list of (doc_id, score) tuples
# TTL: 1 hour (index may be updated)
cache_key = f"search:{hash(query_embedding)}:{k}:{filters}"
```

#### 3. LLM Response Cache
```python
# Cache key: hash of (query + context IDs)
# Value: generated answer JSON
# TTL: 6 hours (answers shouldn't change for same context)
cache_key = f"llm:{hash(query + context_ids)}"
```

### API Design
```python
from src.cache import RedisCache

# Initialize cache
cache = RedisCache(host="localhost", port=6379, db=0)

# Cache query embedding
embedding = embeddings.encode(query)
cache.set(f"emb:{hash(query)}", embedding, ttl=86400)

# Retrieve cached embedding
cached_emb = cache.get(f"emb:{hash(query)}")
if cached_emb is not None:
    print("Cache hit!")

# Cache search results
results = vector_store.search(query_embedding, k=20)
cache.set(f"search:{hash(query_embedding)}:{k}", results, ttl=3600)

# Cache LLM response
answer = llm.generate(query, contexts)
cache.set(f"llm:{hash(query + context_ids)}", answer, ttl=21600)

# Invalidate cache on index update
cache.delete_pattern("search:*")
```

### Performance Targets
- [ ] <5ms cache lookup latency (p99)
- [ ] >80% cache hit rate for popular queries
- [ ] 50% reduction in OpenAI API costs for repeated queries
- [ ] 70% reduction in average query latency

### Cache Metrics
- [ ] Cache hit/miss counters per cache type
- [ ] Average lookup latency
- [ ] Cache memory usage
- [ ] Eviction rate
- [ ] Cost savings (OpenAI API calls avoided)

## Testing Requirements
- [ ] Unit tests for cache operations (set, get, delete)
- [ ] Integration tests with RAG pipeline
- [ ] TTL expiration tests
- [ ] Cache invalidation tests
- [ ] Performance benchmarks (latency with/without cache)

## Documentation
- [ ] Cache architecture diagram
- [ ] TTL configuration guide
- [ ] Cache invalidation strategy
- [ ] Monitoring and metrics guide
- [ ] Redis setup guide (Docker Compose)

## Dependencies
- redis>=4.5.0 (Python client)
- redis-server (for local development)
- Docker (for containerized Redis)

## Acceptance Criteria
- [ ] Redis connection pooling works
- [ ] All cache types implemented with proper TTLs
- [ ] Cache hit rate >80% for repeated queries
- [ ] Query latency reduced by >70% for cached queries
- [ ] Cache invalidation works on index updates
- [ ] All tests pass
- [ ] Documentation complete with examples

## Related Issues
- Related to: FastAPI server (✅ COMPLETE)
- Related to: Query optimization and performance tuning

## References
- Redis Python client: https://redis-py.readthedocs.io/
- Redis caching patterns: https://redis.io/docs/manual/patterns/
- RAG caching strategies: https://www.pinecone.io/learn/retrieval-augmented-generation/
