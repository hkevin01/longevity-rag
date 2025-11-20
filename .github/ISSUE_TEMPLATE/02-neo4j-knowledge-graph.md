---
name: Neo4j Knowledge Graph Integration
about: Integrate Neo4j for structured biomedical knowledge representation
title: '[FEATURE] Implement Neo4j knowledge graph'
labels: enhancement, phase-2, knowledge-graph
assignees: ''
---

## Description
Implement Neo4j knowledge graph integration to represent entities, relationships, and pathways extracted from PubMed literature.

## Current Status
⏳ **TODO** - Stub implementation exists in `src/knowledge_graph/graph_client.py`

## Requirements

### Core Features
- [ ] Neo4j connection management with connection pooling
- [ ] Schema definition for biomedical entities
  - [ ] Compound nodes (name, SMILES, PubChem ID, MOA)
  - [ ] Biomarker nodes (name, type, normal range, unit)
  - [ ] Pathway nodes (name, pathway DB ID, category)
  - [ ] Study nodes (PMID, title, year, journal)
- [ ] Relationship types
  - [ ] MODULATES (Compound -> Biomarker)
  - [ ] AFFECTS (Compound -> Pathway)
  - [ ] ASSOCIATED_WITH (Biomarker -> Disease)
  - [ ] CITED_IN (Entity -> Study)
- [ ] CRUD operations for entities and relationships
- [ ] Cypher query builder for complex graph queries
- [ ] Transaction management for batch inserts

### Graph Query Examples
```cypher
// Find compounds that modulate specific biomarkers
MATCH (c:Compound)-[r:MODULATES]->(b:Biomarker {name: "mTOR"})
RETURN c.name, r.effect_type, r.confidence

// Find shared mechanisms between compounds
MATCH (c1:Compound)-[:AFFECTS]->(p:Pathway)<-[:AFFECTS]-(c2:Compound)
WHERE c1.name = "Rapamycin"
RETURN c2.name, p.name, p.category

// Find biomarker-pathway connections
MATCH (b:Biomarker)-[:ASSOCIATED_WITH]->(p:Pathway)-[:AFFECTS]-(c:Compound)
WHERE b.type = "inflammatory"
RETURN c.name, COUNT(DISTINCT p) as pathway_count
ORDER BY pathway_count DESC
```

### API Design
```python
from src.knowledge_graph import GraphClient, Compound, Biomarker, Pathway

# Initialize client
client = GraphClient(uri="bolt://localhost:7687", user="neo4j", password="password")

# Create entities
compound = Compound(name="Rapamycin", pubchem_id="5284616", moa="mTOR inhibitor")
client.create_node(compound)

biomarker = Biomarker(name="mTOR", type="protein", pathway="PI3K/AKT/mTOR")
client.create_node(biomarker)

# Create relationship
client.create_relationship(compound, "MODULATES", biomarker, 
                          properties={"effect": "inhibits", "confidence": 0.95})

# Query
results = client.run_query("""
  MATCH (c:Compound)-[r:MODULATES]->(b:Biomarker)
  WHERE b.name = $biomarker_name
  RETURN c.name, r.confidence
""", biomarker_name="mTOR")
```

### Integration Points
- [ ] Integrate with NER pipeline to populate entities
- [ ] Extract relationships from relation extraction model
- [ ] Link to PubMed citations for provenance
- [ ] Integrate graph queries into RAG retrieval (hybrid search)

### Performance Targets
- [ ] <50ms query latency for simple traversals (1-2 hops)
- [ ] Support for 100k+ entities and 1M+ relationships
- [ ] Batch insert throughput: 10k entities/second

## Testing Requirements
- [ ] Unit tests for CRUD operations
- [ ] Integration tests with Neo4j test container
- [ ] Query performance benchmarks
- [ ] Schema validation tests
- [ ] Transaction rollback tests

## Documentation
- [ ] Schema documentation with ER diagram
- [ ] Query cookbook with common patterns
- [ ] Setup guide (Docker Compose, Neo4j Desktop)
- [ ] Performance tuning guide (indexes, constraints)

## Dependencies
- neo4j>=5.0.0 (Python driver)
- Docker or Neo4j Desktop for local development
- Testcontainers-python (for integration tests)

## Acceptance Criteria
- [ ] Neo4j connection management works with connection pooling
- [ ] All entity types and relationships can be created/queried
- [ ] Batch insert performance meets targets
- [ ] Integration with NER/RE pipeline complete
- [ ] All tests pass
- [ ] Documentation complete with query examples

## Related Issues
- Depends on: BioClinicalBERT NER implementation (#03)
- Related to: RAG core implementation (✅ COMPLETE)
- Related to: Hybrid retrieval (vector + graph)

## References
- Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual/current/
- Biomedical Knowledge Graphs: https://academic.oup.com/bib/article/22/2/1568/5893345
