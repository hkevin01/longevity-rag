"""Custom exception hierarchy for longevity-rag.

This module defines a hierarchy of exceptions used throughout the application
for better error handling, logging, and user feedback.

Usage:
    from src.utils.errors import IndexNotFoundError
    
    if not index_path.exists():
        raise IndexNotFoundError(f"Index not found at {index_path}")
"""

from __future__ import annotations

from typing import Optional


class LongevityRAGError(Exception):
    """Base exception for all longevity-rag errors.
    
    All custom exceptions in this application should inherit from this class.
    This allows catching all application-specific errors with a single except clause.
    
    Attributes:
        message: Human-readable error message
        details: Optional dict with additional context (file paths, parameters, etc.)
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} [{details_str}]"
        return self.message


# === Data/File Errors ===

class IndexNotFoundError(LongevityRAGError):
    """Raised when vector index file is not found.
    
    Example:
        raise IndexNotFoundError(
            "FAISS index not found",
            details={"path": "/path/to/index", "suggestion": "Run ingest_sample.py first"}
        )
    """
    pass


class MetadataNotFoundError(LongevityRAGError):
    """Raised when metadata file is not found or is empty."""
    pass


class CorruptedDataError(LongevityRAGError):
    """Raised when data file is corrupted or cannot be parsed."""
    pass


class PersistenceError(LongevityRAGError):
    """Raised when saving or loading data fails."""
    pass


# === Validation Errors ===

class ValidationError(LongevityRAGError):
    """Base class for input validation errors."""
    pass


class InvalidParameterError(ValidationError):
    """Raised when a parameter value is invalid.
    
    Example:
        raise InvalidParameterError(
            "k must be positive",
            details={"parameter": "k", "value": -5, "constraint": "> 0"}
        )
    """
    pass


class EmptyInputError(ValidationError):
    """Raised when required input is empty or None."""
    pass


class InputTooLargeError(ValidationError):
    """Raised when input exceeds size limits."""
    pass


class InvalidShapeError(ValidationError):
    """Raised when array/tensor has invalid shape."""
    pass


# === Model/API Errors ===

class EmbeddingError(LongevityRAGError):
    """Base class for embedding-related errors."""
    pass


class ModelLoadError(EmbeddingError):
    """Raised when ML model fails to load."""
    pass


class EncodingError(EmbeddingError):
    """Raised when text encoding fails."""
    pass


class LLMError(LongevityRAGError):
    """Base class for LLM generation errors."""
    pass


class APIKeyError(LLMError):
    """Raised when API key is missing or invalid."""
    pass


class RateLimitError(LLMError):
    """Raised when API rate limit is exceeded."""
    pass


class GenerationError(LLMError):
    """Raised when LLM text generation fails."""
    pass


# === Resource Errors ===

class ResourceError(LongevityRAGError):
    """Base class for resource-related errors (memory, disk, etc.)."""
    pass


class OutOfMemoryError(ResourceError):
    """Raised when operation runs out of memory."""
    pass


class DiskFullError(ResourceError):
    """Raised when disk space is insufficient."""
    pass


class TimeoutError(ResourceError):
    """Raised when operation exceeds time limit."""
    pass


# === Search/Query Errors ===

class SearchError(LongevityRAGError):
    """Base class for search-related errors."""
    pass


class EmptyIndexError(SearchError):
    """Raised when attempting to search an empty index."""
    pass


class QueryError(LongevityRAGError):
    """Raised when query execution fails."""
    pass


# === Configuration Errors ===

class ConfigurationError(LongevityRAGError):
    """Raised when configuration is invalid or missing."""
    pass


# Convenience mapping for error codes
ERROR_CODES = {
    "INDEX_NOT_FOUND": IndexNotFoundError,
    "METADATA_NOT_FOUND": MetadataNotFoundError,
    "CORRUPTED_DATA": CorruptedDataError,
    "INVALID_PARAMETER": InvalidParameterError,
    "EMPTY_INPUT": EmptyInputError,
    "INPUT_TOO_LARGE": InputTooLargeError,
    "MODEL_LOAD_FAILED": ModelLoadError,
    "ENCODING_FAILED": EncodingError,
    "API_KEY_MISSING": APIKeyError,
    "RATE_LIMIT": RateLimitError,
    "OUT_OF_MEMORY": OutOfMemoryError,
    "TIMEOUT": TimeoutError,
}


def raise_error(error_code: str, message: str, details: Optional[dict] = None):
    """Raise an error by error code.
    
    Args:
        error_code: Error code from ERROR_CODES
        message: Human-readable error message
        details: Optional context dict
        
    Raises:
        Corresponding exception type
        
    Example:
        raise_error("INVALID_PARAMETER", "k must be positive", {"k": -5})
    """
    error_class = ERROR_CODES.get(error_code, LongevityRAGError)
    raise error_class(message, details)
