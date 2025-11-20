---
name: BioClinicalBERT NER Implementation
about: Implement named entity recognition using BioClinicalBERT
title: '[FEATURE] Implement BioClinicalBERT NER'
labels: enhancement, phase-2, nlp
assignees: ''
---

## Description
Implement named entity recognition (NER) pipeline using BioClinicalBERT to extract biomedical entities from PubMed abstracts.

## Current Status
⏳ **TODO** - Stub implementation exists in `src/nlp/ner.py`

## Requirements

### Core Features
- [ ] BioClinicalBERT model loading (emilyalsentzer/Bio_ClinicalBERT)
- [ ] Token classification for biomedical entity types:
  - [ ] COMPOUND (drugs, supplements, small molecules)
  - [ ] BIOMARKER (proteins, genes, metabolites)
  - [ ] PATHWAY (biological pathways, signaling cascades)
  - [ ] DISEASE (diseases, conditions, symptoms)
  - [ ] DOSAGE (dosage information, concentrations)
- [ ] Entity span extraction with confidence scores
- [ ] Entity linking to external ontologies (optional)
  - [ ] PubChem for compounds
  - [ ] UniProt for proteins
  - [ ] KEGG for pathways
- [ ] Batch processing for efficiency

### Model Options
**Primary Model:**
- emilyalsentzer/Bio_ClinicalBERT (fine-tuned on MIMIC-III clinical notes)

**Alternative Models:**
- microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext (PubMed + PMC)
- allenai/scibert_scivocab_uncased (scientific text)
- cambridgeltl/SapBERT-from-PubMedBERT-fulltext (entity linking)

### API Design
```python
from src.nlp.ner import BioNER

# Initialize NER model
ner = BioNER(model_name="emilyalsentzer/Bio_ClinicalBERT", device="cuda")

# Extract entities
text = """
Rapamycin (sirolimus) is an mTOR inhibitor that extends lifespan in mice.
It modulates autophagy and reduces inflammation by inhibiting the PI3K/AKT/mTOR pathway.
"""

entities = ner.extract_entities(text)
# Returns: [
#   {"text": "Rapamycin", "type": "COMPOUND", "start": 0, "end": 9, "confidence": 0.98},
#   {"text": "mTOR", "type": "BIOMARKER", "start": 28, "end": 32, "confidence": 0.95},
#   {"text": "PI3K/AKT/mTOR pathway", "type": "PATHWAY", "start": 120, "end": 141, "confidence": 0.92}
# ]

# Batch processing
documents = [text1, text2, text3]
batch_entities = ner.extract_entities_batch(documents, batch_size=8)
```

### Training Data Sources (Optional Fine-tuning)
- [ ] BC5CDR (chemicals and diseases)
- [ ] NCBI-disease corpus
- [ ] JNLPBA (genes and proteins)
- [ ] LitCoin (pathway and mechanism extraction)

### Integration Points
- [ ] Integrate into ingestion pipeline (`scripts/ingest_sample.py`)
- [ ] Store extracted entities in metadata
- [ ] Feed entities into Neo4j knowledge graph
- [ ] Use entities for query expansion in retrieval

### Performance Targets
- [ ] <100ms inference time per document (512 tokens)
- [ ] >90% F1 score on BC5CDR test set (chemicals)
- [ ] >85% F1 score on custom longevity corpus

## Testing Requirements
- [ ] Unit tests for entity extraction
- [ ] Benchmark tests on BC5CDR corpus
- [ ] Integration tests with ingestion pipeline
- [ ] Edge case tests (long documents, special characters)
- [ ] Performance tests (latency, throughput)

## Documentation
- [ ] Model selection guide (BioClinicalBERT vs alternatives)
- [ ] Entity type definitions with examples
- [ ] Fine-tuning guide for custom datasets
- [ ] Troubleshooting common issues (entity boundary errors, low confidence)

## Dependencies
- transformers>=4.30.0
- torch>=2.0.0
- spacy>=3.5.0 (for entity linking, optional)
- scispacy>=0.5.0 (for biomedical entity linking, optional)

## Acceptance Criteria
- [ ] BioClinicalBERT model loads and runs inference
- [ ] Extracts all entity types with >85% F1 score
- [ ] Batch processing works efficiently
- [ ] Integration with ingestion pipeline complete
- [ ] All tests pass
- [ ] Documentation complete with examples

## Related Issues
- Related to: PubMedBERT embeddings (✅ COMPLETE)
- Feeds into: Neo4j knowledge graph (#02)
- Related to: Relation extraction (future work)

## References
- BioClinicalBERT paper: https://arxiv.org/abs/1904.03323
- BC5CDR dataset: https://www.ncbi.nlm.nih.gov/research/bionlp/Data/
- Hugging Face token classification: https://huggingface.co/docs/transformers/tasks/token_classification
