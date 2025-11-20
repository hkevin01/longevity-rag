"""LLM generator wrapper supporting OpenAI and mock modes.

This module provides `LLMGenerator` with two modes:
1. OpenAI mode: Uses OpenAI API (gpt-4 or gpt-3.5-turbo) with OPENAI_API_KEY env var
2. Mock mode: Returns a simple synthesized response for testing

Usage:
    # OpenAI mode (requires OPENAI_API_KEY in environment)
    gen = LLMGenerator(provider="openai", model="gpt-4")
    answer = gen.generate(prompt)

    # Mock mode (for testing)
    gen = LLMGenerator(provider="mock")
    answer = gen.generate(prompt)
"""

from __future__ import annotations

from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False
    logger.warning(
        "openai package not available. Install with: pip install openai. "
        "Falling back to mock generator."
    )


class LLMGenerator:
    """LLM generator supporting OpenAI API or mock mode.

    Args:
        provider: "openai" or "mock" (default: "mock")
        model: OpenAI model name (default: "gpt-4")
        api_key: OpenAI API key (default: reads from OPENAI_API_KEY env var)
        temperature: Sampling temperature (0.0-1.0, default 0.7)
        max_tokens: Maximum tokens in response (default: 512)
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ):
        self.provider = provider or "mock"
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        if self.provider == "openai":
            if not _OPENAI_AVAILABLE:
                logger.error("OpenAI provider requested but openai package not installed. Falling back to mock.")
                self.provider = "mock"
            else:
                api_key = api_key or os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    logger.error("OPENAI_API_KEY not found in environment. Falling back to mock.")
                    self.provider = "mock"
                else:
                    try:
                        self.client = OpenAI(api_key=api_key)
                        logger.info(f"OpenAI LLM generator initialized with model: {self.model}")
                    except Exception as e:
                        logger.error(f"Failed to initialize OpenAI client: {e}. Falling back to mock.")
                        self.provider = "mock"

        if self.provider == "mock":
            logger.info("Using mock LLM generator")

    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate text response from prompt.

        Args:
            prompt: Input prompt with context and question
            max_tokens: Override max_tokens for this call

        Returns:
            Generated text response
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, max_tokens)
        else:
            return self._generate_mock(prompt)

    def _generate_openai(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a scientific research assistant specializing in longevity and aging research. "
                                   "Provide accurate, evidence-based answers with citations to PubMed IDs (PMIDs) when available. "
                                   "Be concise but comprehensive."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"[Error generating response: {e}]"

    def _generate_mock(self, prompt: str) -> str:
        """Mock generator for testing."""
        pmids = []
        for token in prompt.split():
            if token.startswith("PMID:"):
                pmids.append(token)

        base = "(Mock answer) Based on the retrieved evidence, this is a synthesized response. "
        base += "In real mode, this would be a comprehensive answer from GPT-4 or another LLM."
        if pmids:
            base += " Relevant papers: " + ", ".join(pmids[:3])
        return base

    def __repr__(self):
        return f"LLMGenerator(provider={self.provider}, model={self.model if self.provider == 'openai' else 'N/A'})"

