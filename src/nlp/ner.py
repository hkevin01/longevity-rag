"""NER interface stub using BioClinicalBERT (placeholder).

This module exposes `extract_entities(text)` which returns a list of
entity dicts: {text, label, start, end}. Replace with a real model when
available (BioClinicalBERT fine-tuned NER).
"""

from __future__ import annotations

from typing import List, Dict


def extract_entities(text: str) -> List[Dict]:
    # Placeholder: return empty list for MVP
    return []

