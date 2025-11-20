"""LLM generator wrapper.

This module provides a small interface `LLMGenerator` with a `generate` method.
For the MVP it returns a short mocked answer which references found PMIDs if
present in the prompt. Replace with real LLM provider (OpenAI, local Llama, etc.)
by implementing the `generate` method.
"""

from __future__ import annotations

from typing import Optional


class LLMGenerator:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or "mock"

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        # Very small mock: report that the answer is synthesized and echo PMIDs
        pmids = []
        for token in prompt.split():
            if token.startswith("PMID:"):
                pmids.append(token)

        base = "(Mocked answer) Synthesized response based on retrieved evidence."
        if pmids:
            base += " Cited: " + ", ".join(pmids)
        return base

