# GitHub Issues for Longevity RAG Project

These are the recommended issues to create in the GitHub repository to track remaining MVP and Phase 1+ features.

---

## Issue #1: Implement BioClinicalBERT NER for Entity Extraction

**Title:** feat: Implement BioClinicalBERT NER for entity extraction

**Labels:** `enhancement`, `nlp`, `phase-3`

**Description:**

Implement named entity recognition (NER) using BioClinicalBERT to extract biomedical entities from text.

**Current State:**
- Stub implementation in `src/nlp/ner.py` returns empty list
- Module is imported but not functional

**Requirements:**
- [ ] Load BioClinicalBERT model from HuggingFace
- [ ] Implement `extract_entities(text)` function
- [ ] Return entities with: `{text, label, start, end, confidence}`
- [ ] Support entity types: DRUG, PATHWAY, ORGANISM, OUTCOME, BIOMARKER, GENE
- [ ] Add batch processing support
- [ ] Write unit tests with sample biomedical text
- [ ] Achieve F1 score > 0.85 on biomedical NER benchmark

**Acceptance Criteria:**
- BioClinicalBERT model loads and runs inference
- Entities extracted from sample abstracts with high accuracy
- Tests pass with >85% F1 score
- Documentation updated with usage examples

**References:**
- Model: https://huggingface.co/emilyalsentzer/Bio_ClinicalBERT
- Related: `docs/project-plan.md` Phase 3

---

## Issue #2: Implement Cross-Encoder Reranking

**Title:** feat: Add cross-encoder reranking to RAG pipeline

**Labels:** `enhancement`, `rag`, `phase-2`

**Description:**

Improve retrieval quality by adding a cross-encoder reranking step after initial FAISS retrieval.

**Current State:**
- RAG pipeline uses only vector similarity (cosine) for ranking
- No reranking step implemented

**Requirements:**
- [ ] Add cross-encoder model (e.g., `ms-marco-MiniLM-L-6-v2`)
- [ ] Integrate reranking in `src/rag/core.py` after vector retrieval
- [ ] Rerank top-k results (k=100 → top 10)
- [ ] Add configuration option to enable/disable reranking
- [ ] Benchmark: measure recall improvement
- [ ] Document performance trade-offs (accuracy vs. latency)

**Acceptance Criteria:**
- Cross-encoder reranks retrieved chunks
- Recall@10 improves by at least 10%
- Latency increase documented and acceptable (<2s total)
- Tests validate reranking logic

**References:**
- Model: https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2
- README mentions: "Optional cross-encoder reranking"

---

## Issue #3: Implement Neo4j Knowledge Graph Integration

**Title:** feat: Integrate Neo4j knowledge graph for multi-hop reasoning

**Labels:** `enhancement`, `knowledge-graph`, `phase-2`

**Description:**

Build Neo4j knowledge graph from extracted entities and relations to enable multi-hop reasoning.

**Current State:**
- Stub implementation in `src/knowledge_graph/graph_client.py`
- Schema defined in `src/knowledge_graph/schema.py`
- No actual Neo4j integration

**Requirements:**
- [ ] Implement `GraphClient` class with Neo4j connection
- [ ] Create nodes: INTERVENTION, STUDY, OUTCOME, PATHWAY, PAPER
- [ ] Create relationships: MODULATES, EXTENDS, ASSOCIATES_WITH
- [ ] Implement ingestion pipeline: extract → NER → relations → Neo4j
- [ ] Add Cypher query templates for common questions
- [ ] Support multi-hop queries (e.g., intervention → pathway → outcome)
- [ ] Add graph expansion to RAG pipeline
- [ ] Write integration tests with test database

**Acceptance Criteria:**
- Neo4j database populated with entities and relations
- Multi-hop queries return expected results
- Graph expansion improves RAG answer quality
- Tests pass with test Neo4j instance

**References:**
- `docs/project-plan.md` Phase 2
- README describes 35k+ entities, 250k+ relationships

---

## Issue #4: Implement Redis Caching Layer

**Title:** feat: Add Redis caching for query results and embeddings

**Labels:** `enhancement`, `performance`, `phase-4`

**Description:**

Add Redis caching to improve query latency and reduce redundant computations.

**Current State:**
- No caching implemented
- Every query recomputes embeddings and searches index

**Requirements:**
- [ ] Add Redis client in `src/utils/cache.py`
- [ ] Cache query embeddings (key: hash(query), value: embedding vector)
- [ ] Cache query results (key: hash(query+k), value: result JSON)
- [ ] Add TTL configuration (default: 1 hour for results, 1 day for embeddings)
- [ ] Add cache invalidation on index rebuild
- [ ] Add metrics: cache hit rate, latency improvement
- [ ] Make Redis optional (graceful fallback if not configured)

**Acceptance Criteria:**
- Redis caching reduces query latency by >50% for cached queries
- Cache hit rate >80% for repeated queries
- System works without Redis (fallback to no-cache mode)
- Tests verify caching behavior

**References:**
- README mentions: "Redis for caching"
- Target: 99% cache hit rate for common queries

---

## Issue #5: Implement PubMed E-utilities API Client

**Title:** feat: Implement PubMed E-utilities API client for automated data fetch

**Labels:** `enhancement`, `data`, `phase-1`

**Description:**

Build a PubMed API client using E-utilities to automatically fetch and ingest papers.

**Current State:**
- Stub in `src/utils/pubmed_client.py` only reads local files
- No API integration

**Requirements:**
- [ ] Implement E-utilities wrapper (ESearch, EFetch)
- [ ] Support keyword search with filters (publication date, MeSH terms)
- [ ] Respect rate limits (3 requests/second without API key)
- [ ] Add retry logic with exponential backoff
- [ ] Parse XML responses (abstract, metadata, authors, citations)
- [ ] Store raw XML in `data/raw/pubmed/`
- [ ] Add CLI tool: `scripts/fetch_pubmed.py --query "rapamycin aging" --max 1000`
- [ ] Write integration tests (mock API responses)

**Acceptance Criteria:**
- Successfully fetch 1000+ papers on aging keywords
- XML parsed correctly with metadata extracted
- Rate limiting prevents API abuse
- Tests pass with mocked API responses

**References:**
- `docs/project-plan.md` Phase 1
- E-utilities docs: https://www.ncbi.nlm.nih.gov/books/NBK25501/

---

## Issue #6: Implement Database Schema with SQLAlchemy

**Title:** feat: Implement PostgreSQL database schema for papers and metadata

**Labels:** `enhancement`, `database`, `phase-1`

**Description:**

Design and implement relational database schema for storing papers, authors, and metadata.

**Current State:**
- Metadata stored only in JSONL file (`data/processed/metadata.jsonl`)
- No structured database

**Requirements:**
- [ ] Create SQLAlchemy models in `src/database/models.py`
- [ ] Tables: papers, authors, citations, chunks, embeddings
- [ ] Add indexes for fast search (pmid, publication_date, journal)
- [ ] Create Alembic migrations
- [ ] Implement data access layer (DAO/repository pattern)
- [ ] Add connection pooling
- [ ] Write CRUD operations with tests
- [ ] Integrate with ingestion pipeline

**Acceptance Criteria:**
- Database schema created with proper relationships
- Migrations run successfully
- 10k+ papers stored with sub-100ms query time
- Tests verify CRUD operations

**References:**
- `docs/project-plan.md` Phase 1
- Requirements: SQLAlchemy>=2.0.0, Alembic>=1.11.0

---

## Issue #7: Add Comprehensive Integration Tests

**Title:** test: Add end-to-end integration tests for RAG pipeline

**Labels:** `testing`, `quality`

**Description:**

Create comprehensive integration tests for the full RAG pipeline.

**Current State:**
- Unit tests exist for chunking and individual components
- No end-to-end integration tests

**Requirements:**
- [ ] Test full pipeline: ingest → embed → search → generate
- [ ] Test with real sample data (10-20 papers)
- [ ] Verify answer quality (BLEU score, citation accuracy)
- [ ] Test error handling (missing index, API failures)
- [ ] Test concurrent queries (stress test)
- [ ] Add performance benchmarks (latency, throughput)
- [ ] Run in CI pipeline
- [ ] Document test coverage target (>85%)

**Acceptance Criteria:**
- Integration tests cover happy path and error cases
- Tests run in <60 seconds
- All tests pass in CI
- Code coverage >85%

---

## Issue #8: Implement Automated Meta-Analysis for Biomarkers

**Title:** feat: Add biomarker meta-analysis module

**Labels:** `enhancement`, `biomarkers`, `phase-5`

**Description:**

Implement statistical meta-analysis for aggregating biomarker effect sizes across studies.

**Current State:**
- Stub in `src/biomarkers/analysis.py` returns simple average
- No real meta-analysis

**Requirements:**
- [ ] Implement random-effects model (DerSimonian-Laird)
- [ ] Calculate I² statistic (heterogeneity)
- [ ] Detect publication bias (Egger's test, funnel plots)
- [ ] Forest plot generation
- [ ] Support subgroup analysis (by organism, age, intervention)
- [ ] Add confidence intervals (95% CI)
- [ ] Integrate with knowledge graph (query by biomarker)

**Acceptance Criteria:**
- Meta-analysis produces valid effect sizes
- I² correctly measures heterogeneity
- Publication bias detection works
- Visualizations generate correctly
- Tests verify statistical correctness

**References:**
- `docs/project-plan.md` Phase 5
- README mentions: "Combine effect sizes across studies (random-effects model)"

---

## Issue #9: Create Web UI / Dashboard

**Title:** feat: Create interactive web UI for querying and visualization

**Labels:** `enhancement`, `ui`, `phase-6`

**Description:**

Build a web interface for non-technical users to query the RAG system.

**Current State:**
- FastAPI server provides REST API
- No user-facing web interface

**Requirements:**
- [ ] React/Vue.js frontend
- [ ] Query input with autocomplete
- [ ] Display answers with expandable citations
- [ ] Show confidence scores and metadata
- [ ] Knowledge graph visualization (D3.js or Cytoscape)
- [ ] Search history and saved queries
- [ ] Export results (PDF, CSV, JSON)
- [ ] Mobile-responsive design

**Acceptance Criteria:**
- Web UI loads and queries backend successfully
- Results displayed clearly with citations
- Graph visualization works
- Mobile-friendly responsive design
- Deployed and accessible

**References:**
- `docs/project-plan.md` Phase 6
- README mentions: "Analytics Dashboard"

---

## Issue #10: Add Docker Compose Multi-Service Setup

**Title:** infra: Complete docker-compose.yml with all services

**Labels:** `infrastructure`, `docker`

**Description:**

Complete the Docker Compose setup with all required services.

**Current State:**
- `docker-compose.yml` defines PostgreSQL, Neo4j, Redis
- No longevity-rag service definition
- Services not connected

**Requirements:**
- [ ] Add longevity-rag service to docker-compose.yml
- [ ] Configure service dependencies (depends_on)
- [ ] Add health checks for all services
- [ ] Set up volume mounts for data persistence
- [ ] Configure environment variables via .env
- [ ] Add initialization scripts (init.sql, init-neo4j.cypher)
- [ ] Document startup sequence
- [ ] Test multi-container orchestration

**Acceptance Criteria:**
- `docker-compose up` starts all services
- Services communicate correctly
- Data persists after restart
- Documentation covers common scenarios

**References:**
- Existing: `docker-compose.yml`, `Dockerfile`

---

## Priority Order for MVP → Phase 1:

1. **Issue #5** (PubMed API client) - Critical for data ingestion
2. **Issue #6** (Database schema) - Foundation for data management
3. **Issue #7** (Integration tests) - Quality assurance
4. **Issue #2** (Cross-encoder reranking) - Immediate RAG improvement
5. **Issue #4** (Redis caching) - Performance optimization
6. **Issue #3** (Neo4j KG) - Advanced reasoning
7. **Issue #1** (BioClinicalBERT NER) - NLP enhancement
8. **Issue #8** (Meta-analysis) - Biomarker features
9. **Issue #10** (Docker Compose) - Infrastructure
10. **Issue #9** (Web UI) - User experience

---

## How to Create These Issues in GitHub:

```bash
# Use GitHub CLI (requires gh installed and authenticated)
gh issue create --title "feat: Implement BioClinicalBERT NER for entity extraction" \
  --body-file <(cat <<EOF
[Copy description from Issue #1 above]
