"""Minimal PubMed client for local sample ingestion.

This helper expects pre-downloaded PubMed files in `data/raw/sample_pubmed/`.
For MVP it will read simple JSONL files or plain text files with title+abstract.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict


def list_sample_files(data_dir: str = "data/raw/sample_pubmed") -> List[Path]:
    p = Path(data_dir)
    if not p.exists():
        return []
    return [x for x in p.iterdir() if x.is_file()]


def parse_sample_file(path: Path) -> Dict:
    """Parse a single sample file. Accepts JSON (with title/abstract/pmid) or
    a simple text file where first line is title and the rest is abstract.
    """
    try:
        import json
        raw = path.read_text(encoding="utf8")
        data = json.loads(raw)
        return {"title": data.get("title"), "abstract": data.get("abstract"), "pmid": data.get("pmid")}
    except Exception:
        txt = path.read_text(encoding="utf8").strip().splitlines()
        title = txt[0] if txt else ""
        abstract = "\n".join(txt[1:]) if len(txt) > 1 else ""
        return {"title": title, "abstract": abstract, "pmid": None}

