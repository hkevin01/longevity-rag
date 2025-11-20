"""Input validation utilities for longevity-rag.

This module provides reusable validation functions to ensure inputs meet
expected constraints. All functions raise appropriate exceptions from
src.utils.errors when validation fails.

Usage:
    from src.utils.validation import validate_positive_int, validate_not_empty
    
    def search(query: str, k: int):
        validate_not_empty(query, "query")
        validate_positive_int(k, "k")
        # ... proceed with search
"""

from __future__ import annotations

from typing import Any, List, Optional, Union
import numpy as np

from src.utils.errors import (
    InvalidParameterError,
    EmptyInputError,
    InputTooLargeError,
    InvalidShapeError,
)


# === General Validators ===

def validate_not_none(value: Any, param_name: str) -> None:
    """Validate that value is not None.
    
    Args:
        value: Value to check
        param_name: Parameter name for error message
        
    Raises:
        EmptyInputError: If value is None
        
    Example:
        validate_not_none(query, "query")
    """
    if value is None:
        raise EmptyInputError(
            f"{param_name} cannot be None",
            details={"parameter": param_name, "value": None}
        )


def validate_not_empty(value: Union[str, list, dict, np.ndarray], param_name: str) -> None:
    """Validate that value is not empty (works for str, list, dict, array).
    
    Args:
        value: Value to check
        param_name: Parameter name for error message
        
    Raises:
        EmptyInputError: If value is empty or None
        
    Example:
        validate_not_empty(query, "query")
        validate_not_empty(texts, "texts")
    """
    validate_not_none(value, param_name)
    
    if isinstance(value, str) and len(value.strip()) == 0:
        raise EmptyInputError(
            f"{param_name} cannot be empty string",
            details={"parameter": param_name}
        )
    
    if isinstance(value, (list, dict)) and len(value) == 0:
        raise EmptyInputError(
            f"{param_name} cannot be empty {type(value).__name__}",
            details={"parameter": param_name, "type": type(value).__name__}
        )
    
    if isinstance(value, np.ndarray) and value.size == 0:
        raise EmptyInputError(
            f"{param_name} cannot be empty array",
            details={"parameter": param_name, "shape": value.shape}
        )


def validate_max_length(value: Union[str, list, np.ndarray], param_name: str, max_length: int) -> None:
    """Validate that value does not exceed max length.
    
    Args:
        value: Value to check
        param_name: Parameter name for error message
        max_length: Maximum allowed length
        
    Raises:
        InputTooLargeError: If value exceeds max_length
        
    Example:
        validate_max_length(query, "query", 10000)
    """
    actual_length = len(value)
    if actual_length > max_length:
        raise InputTooLargeError(
            f"{param_name} exceeds maximum length",
            details={
                "parameter": param_name,
                "actual": actual_length,
                "max": max_length
            }
        )


# === Numeric Validators ===

def validate_positive_int(value: int, param_name: str) -> None:
    """Validate that value is a positive integer.
    
    Args:
        value: Value to check
        param_name: Parameter name for error message
        
    Raises:
        InvalidParameterError: If value is not positive integer
        
    Example:
        validate_positive_int(k, "k")
    """
    if not isinstance(value, int):
        raise InvalidParameterError(
            f"{param_name} must be an integer",
            details={"parameter": param_name, "value": value, "type": type(value).__name__}
        )
    
    if value <= 0:
        raise InvalidParameterError(
            f"{param_name} must be positive",
            details={"parameter": param_name, "value": value, "constraint": "> 0"}
        )


def validate_non_negative_int(value: int, param_name: str) -> None:
    """Validate that value is a non-negative integer (>= 0).
    
    Args:
        value: Value to check
        param_name: Parameter name for error message
        
    Raises:
        InvalidParameterError: If value is not non-negative integer
    """
    if not isinstance(value, int):
        raise InvalidParameterError(
            f"{param_name} must be an integer",
            details={"parameter": param_name, "value": value, "type": type(value).__name__}
        )
    
    if value < 0:
        raise InvalidParameterError(
            f"{param_name} must be non-negative",
            details={"parameter": param_name, "value": value, "constraint": ">= 0"}
        )


def validate_range(value: Union[int, float], param_name: str, min_val: Union[int, float], max_val: Union[int, float]) -> None:
    """Validate that value is within specified range [min_val, max_val].
    
    Args:
        value: Value to check
        param_name: Parameter name for error message
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        
    Raises:
        InvalidParameterError: If value is outside range
        
    Example:
        validate_range(temperature, "temperature", 0.0, 1.0)
    """
    if not isinstance(value, (int, float)):
        raise InvalidParameterError(
            f"{param_name} must be numeric",
            details={"parameter": param_name, "value": value, "type": type(value).__name__}
        )
    
    if not (min_val <= value <= max_val):
        raise InvalidParameterError(
            f"{param_name} must be in range [{min_val}, {max_val}]",
            details={
                "parameter": param_name,
                "value": value,
                "min": min_val,
                "max": max_val
            }
        )


def validate_positive_float(value: float, param_name: str) -> None:
    """Validate that value is a positive float.
    
    Args:
        value: Value to check
        param_name: Parameter name for error message
        
    Raises:
        InvalidParameterError: If value is not positive float
    """
    if not isinstance(value, (int, float)):
        raise InvalidParameterError(
            f"{param_name} must be numeric",
            details={"parameter": param_name, "value": value, "type": type(value).__name__}
        )
    
    if value <= 0:
        raise InvalidParameterError(
            f"{param_name} must be positive",
            details={"parameter": param_name, "value": value, "constraint": "> 0"}
        )


# === Array/Shape Validators ===

def validate_array_shape(array: np.ndarray, param_name: str, expected_ndim: int, expected_shape: Optional[tuple] = None) -> None:
    """Validate numpy array shape.
    
    Args:
        array: Array to check
        param_name: Parameter name for error message
        expected_ndim: Expected number of dimensions
        expected_shape: Expected shape (None to skip), use -1 for any size in that dimension
        
    Raises:
        InvalidShapeError: If array shape is invalid
        
    Example:
        validate_array_shape(embeddings, "embeddings", 2, (-1, 768))
    """
    if not isinstance(array, np.ndarray):
        raise InvalidShapeError(
            f"{param_name} must be numpy array",
            details={"parameter": param_name, "type": type(array).__name__}
        )
    
    if array.ndim != expected_ndim:
        raise InvalidShapeError(
            f"{param_name} must be {expected_ndim}D array",
            details={
                "parameter": param_name,
                "actual_ndim": array.ndim,
                "expected_ndim": expected_ndim,
                "shape": array.shape
            }
        )
    
    if expected_shape is not None:
        for i, (actual, expected) in enumerate(zip(array.shape, expected_shape)):
            if expected != -1 and actual != expected:
                raise InvalidShapeError(
                    f"{param_name} has invalid shape at dimension {i}",
                    details={
                        "parameter": param_name,
                        "actual_shape": array.shape,
                        "expected_shape": expected_shape,
                        "dimension": i,
                        "actual": actual,
                        "expected": expected
                    }
                )


def validate_2d_array(array: np.ndarray, param_name: str) -> None:
    """Validate that array is 2D and not empty.
    
    Args:
        array: Array to check
        param_name: Parameter name for error message
        
    Raises:
        InvalidShapeError: If array is not 2D
        EmptyInputError: If array is empty
    """
    validate_not_none(array, param_name)
    validate_array_shape(array, param_name, expected_ndim=2)
    validate_not_empty(array, param_name)


def validate_vector(vector: np.ndarray, param_name: str, expected_dim: Optional[int] = None) -> None:
    """Validate that input is a 1D vector with optional dimension check.
    
    Args:
        vector: Vector to check
        param_name: Parameter name for error message
        expected_dim: Expected dimension (None to skip)
        
    Raises:
        InvalidShapeError: If vector is not 1D or wrong dimension
    """
    validate_not_none(vector, param_name)
    validate_array_shape(vector, param_name, expected_ndim=1)
    
    if expected_dim is not None and vector.shape[0] != expected_dim:
        raise InvalidShapeError(
            f"{param_name} has wrong dimension",
            details={
                "parameter": param_name,
                "actual_dim": vector.shape[0],
                "expected_dim": expected_dim
            }
        )


# === List/Collection Validators ===

def validate_list_of_strings(value: List[str], param_name: str) -> None:
    """Validate that value is a list of strings.
    
    Args:
        value: Value to check
        param_name: Parameter name for error message
        
    Raises:
        InvalidParameterError: If value is not a list of strings
        
    Example:
        validate_list_of_strings(texts, "texts")
    """
    if not isinstance(value, list):
        raise InvalidParameterError(
            f"{param_name} must be a list",
            details={"parameter": param_name, "type": type(value).__name__}
        )
    
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise InvalidParameterError(
                f"{param_name}[{i}] must be a string",
                details={
                    "parameter": param_name,
                    "index": i,
                    "item_type": type(item).__name__
                }
            )


def validate_list_not_empty(value: List[Any], param_name: str) -> None:
    """Validate that list is not empty and all elements are not None.
    
    Args:
        value: List to check
        param_name: Parameter name for error message
        
    Raises:
        EmptyInputError: If list is empty
        InvalidParameterError: If any element is None
    """
    validate_not_empty(value, param_name)
    
    for i, item in enumerate(value):
        if item is None:
            raise InvalidParameterError(
                f"{param_name}[{i}] cannot be None",
                details={"parameter": param_name, "index": i}
            )


# === Bounds Validators ===

def validate_index_bounds(index: int, param_name: str, max_index: int) -> None:
    """Validate that index is within bounds [0, max_index).
    
    Args:
        index: Index to check
        param_name: Parameter name for error message
        max_index: Maximum valid index (exclusive)
        
    Raises:
        InvalidParameterError: If index is out of bounds
        
    Example:
        validate_index_bounds(idx, "idx", len(metadata))
    """
    if not (0 <= index < max_index):
        raise InvalidParameterError(
            f"{param_name} out of bounds",
            details={
                "parameter": param_name,
                "index": index,
                "valid_range": f"[0, {max_index})"
            }
        )


def validate_k_value(k: int, param_name: str, max_k: Optional[int] = None) -> None:
    """Validate k parameter for top-k search.
    
    Args:
        k: k value to check
        param_name: Parameter name for error message (usually "k")
        max_k: Maximum allowed k (e.g., index size), None to skip
        
    Raises:
        InvalidParameterError: If k is invalid
        
    Example:
        validate_k_value(k, "k", len(embeddings))
    """
    validate_positive_int(k, param_name)
    
    if max_k is not None and k > max_k:
        raise InvalidParameterError(
            f"{param_name} exceeds maximum",
            details={
                "parameter": param_name,
                "value": k,
                "max": max_k
            }
        )


# === Type Validators ===

def validate_type(value: Any, param_name: str, expected_type: type) -> None:
    """Validate that value is of expected type.
    
    Args:
        value: Value to check
        param_name: Parameter name for error message
        expected_type: Expected type
        
    Raises:
        InvalidParameterError: If value is wrong type
        
    Example:
        validate_type(temperature, "temperature", float)
    """
    if not isinstance(value, expected_type):
        raise InvalidParameterError(
            f"{param_name} must be {expected_type.__name__}",
            details={
                "parameter": param_name,
                "actual_type": type(value).__name__,
                "expected_type": expected_type.__name__
            }
        )
