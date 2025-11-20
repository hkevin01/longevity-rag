# Scripts Directory

This directory contains utility scripts and examples for the Longevity RAG system.

## Available Scripts

### `example_usage.py`
Demonstrates basic usage of the logging and timing utilities.

**Usage:**
```bash
python scripts/example_usage.py
```

**Features:**
- Timed function execution
- Context manager timing
- Statistical tracking
- Timing reports

## Future Scripts (Planned)

### Data Collection
- `fetch_pubmed_data.py` - Fetch papers from PubMed API
- `scrape_biorxiv.py` - Collect preprints from bioRxiv
- `process_papers.py` - Process and clean collected papers

### Data Processing
- `generate_embeddings.py` - Create vector embeddings for papers
- `build_knowledge_graph.py` - Construct knowledge graph from entities
- `extract_entities.py` - Extract biomedical entities from text

### System Maintenance
- `run_pipeline.py` - Execute full ETL pipeline
- `backup_data.py` - Backup database and embeddings
- `validate_data.py` - Run data quality checks

### Analysis
- `analyze_corpus.py` - Analyze paper corpus statistics
- `evaluate_rag.py` - Evaluate RAG system performance
- `benchmark_models.py` - Benchmark different models

## Adding New Scripts

When adding new scripts:

1. **Follow naming convention**: Use descriptive snake_case names
2. **Add shebang**: `#!/usr/bin/env python3`
3. **Include docstring**: Describe purpose and usage
4. **Add logging**: Use the project's logging utilities
5. **Handle errors**: Implement proper error handling
6. **Update this README**: Document new scripts

## Script Template

```python
#!/usr/bin/env python3
"""
Script description.

Usage:
    python scripts/your_script.py [options]
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logger import setup_logger

logger = setup_logger(name="your_script")


def main():
    """Main function."""
    logger.info("Script started")
    # Your code here
    logger.info("Script completed")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        sys.exit(1)
```

## Notes

- All scripts should be executable: `chmod +x scripts/your_script.py`
- Use environment variables from `.env` for configuration
- Add tests for complex scripts in `tests/` directory
- Consider command-line arguments for flexibility
