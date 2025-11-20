"""Tests for validation utilities and error handling.

This module tests the comprehensive input validation system including
boundary conditions, edge cases, and error scenarios.
"""

import pytest
import numpy as np

from src.utils.validation import (
    validate_not_none,
    validate_not_empty,
    validate_max_length,
    validate_positive_int,
    validate_non_negative_int,
    validate_range,
    validate_positive_float,
    validate_array_shape,
    validate_2d_array,
    validate_vector,
    validate_list_of_strings,
    validate_list_not_empty,
    validate_index_bounds,
    validate_k_value,
    validate_type,
)
from src.utils.errors import (
    EmptyInputError,
    InputTooLargeError,
    InvalidParameterError,
    InvalidShapeError,
)


class TestGeneralValidators:
    """Test general validation functions."""
    
    def test_validate_not_none_success(self):
        """Test validate_not_none with valid input."""
        validate_not_none("hello", "param")
        validate_not_none(0, "param")
        validate_not_none([], "param")
        validate_not_none(False, "param")
    
    def test_validate_not_none_failure(self):
        """Test validate_not_none with None."""
        with pytest.raises(EmptyInputError) as exc_info:
            validate_not_none(None, "param")
        assert "param cannot be None" in str(exc_info.value)
    
    def test_validate_not_empty_string_success(self):
        """Test validate_not_empty with valid strings."""
        validate_not_empty("hello", "param")
        validate_not_empty("  hello  ", "param")
    
    def test_validate_not_empty_string_failure(self):
        """Test validate_not_empty with empty strings."""
        with pytest.raises(EmptyInputError):
            validate_not_empty("", "param")
        
        with pytest.raises(EmptyInputError):
            validate_not_empty("   ", "param")
    
    def test_validate_not_empty_list_success(self):
        """Test validate_not_empty with valid lists."""
        validate_not_empty([1, 2, 3], "param")
        validate_not_empty([None], "param")  # Not empty, contains None
    
    def test_validate_not_empty_list_failure(self):
        """Test validate_not_empty with empty lists."""
        with pytest.raises(EmptyInputError):
            validate_not_empty([], "param")
    
    def test_validate_not_empty_array_success(self):
        """Test validate_not_empty with valid arrays."""
        validate_not_empty(np.array([1, 2, 3]), "param")
    
    def test_validate_not_empty_array_failure(self):
        """Test validate_not_empty with empty arrays."""
        with pytest.raises(EmptyInputError):
            validate_not_empty(np.array([]), "param")
    
    def test_validate_max_length_success(self):
        """Test validate_max_length with valid lengths."""
        validate_max_length("hello", "param", 10)
        validate_max_length("hello", "param", 5)
        validate_max_length([1, 2, 3], "param", 5)
    
    def test_validate_max_length_failure(self):
        """Test validate_max_length with excessive lengths."""
        with pytest.raises(InputTooLargeError) as exc_info:
            validate_max_length("hello world", "param", 5)
        assert "exceeds maximum length" in str(exc_info.value)


class TestNumericValidators:
    """Test numeric validation functions."""
    
    def test_validate_positive_int_success(self):
        """Test validate_positive_int with valid values."""
        validate_positive_int(1, "param")
        validate_positive_int(100, "param")
    
    def test_validate_positive_int_zero_failure(self):
        """Test validate_positive_int with zero."""
        with pytest.raises(InvalidParameterError) as exc_info:
            validate_positive_int(0, "param")
        assert "must be positive" in str(exc_info.value)
    
    def test_validate_positive_int_negative_failure(self):
        """Test validate_positive_int with negative values."""
        with pytest.raises(InvalidParameterError):
            validate_positive_int(-1, "param")
    
    def test_validate_positive_int_type_failure(self):
        """Test validate_positive_int with wrong types."""
        with pytest.raises(InvalidParameterError):
            validate_positive_int(1.5, "param")
        
        with pytest.raises(InvalidParameterError):
            validate_positive_int("1", "param")
    
    def test_validate_non_negative_int_success(self):
        """Test validate_non_negative_int with valid values."""
        validate_non_negative_int(0, "param")
        validate_non_negative_int(1, "param")
        validate_non_negative_int(100, "param")
    
    def test_validate_non_negative_int_failure(self):
        """Test validate_non_negative_int with negative values."""
        with pytest.raises(InvalidParameterError):
            validate_non_negative_int(-1, "param")
    
    def test_validate_range_success(self):
        """Test validate_range with valid values."""
        validate_range(0.5, "param", 0.0, 1.0)
        validate_range(0.0, "param", 0.0, 1.0)
        validate_range(1.0, "param", 0.0, 1.0)
        validate_range(5, "param", 0, 10)
    
    def test_validate_range_failure(self):
        """Test validate_range with out-of-range values."""
        with pytest.raises(InvalidParameterError):
            validate_range(1.5, "param", 0.0, 1.0)
        
        with pytest.raises(InvalidParameterError):
            validate_range(-0.5, "param", 0.0, 1.0)
    
    def test_validate_positive_float_success(self):
        """Test validate_positive_float with valid values."""
        validate_positive_float(0.1, "param")
        validate_positive_float(1.0, "param")
        validate_positive_float(1, "param")  # int is also valid
    
    def test_validate_positive_float_failure(self):
        """Test validate_positive_float with invalid values."""
        with pytest.raises(InvalidParameterError):
            validate_positive_float(0.0, "param")
        
        with pytest.raises(InvalidParameterError):
            validate_positive_float(-0.5, "param")


class TestArrayValidators:
    """Test array validation functions."""
    
    def test_validate_array_shape_success(self):
        """Test validate_array_shape with valid shapes."""
        arr = np.random.randn(10, 768)
        validate_array_shape(arr, "param", 2)
        validate_array_shape(arr, "param", 2, (-1, 768))
        validate_array_shape(arr, "param", 2, (10, -1))
    
    def test_validate_array_shape_wrong_ndim(self):
        """Test validate_array_shape with wrong dimensions."""
        arr = np.random.randn(10)
        with pytest.raises(InvalidShapeError):
            validate_array_shape(arr, "param", 2)
    
    def test_validate_array_shape_wrong_shape(self):
        """Test validate_array_shape with wrong shape."""
        arr = np.random.randn(10, 768)
        with pytest.raises(InvalidShapeError):
            validate_array_shape(arr, "param", 2, (10, 512))
    
    def test_validate_2d_array_success(self):
        """Test validate_2d_array with valid arrays."""
        arr = np.random.randn(10, 768)
        validate_2d_array(arr, "param")
    
    def test_validate_2d_array_wrong_dim(self):
        """Test validate_2d_array with wrong dimensions."""
        arr = np.random.randn(10)
        with pytest.raises(InvalidShapeError):
            validate_2d_array(arr, "param")
    
    def test_validate_2d_array_empty(self):
        """Test validate_2d_array with empty arrays."""
        arr = np.array([]).reshape(0, 768)
        with pytest.raises(EmptyInputError):
            validate_2d_array(arr, "param")
    
    def test_validate_vector_success(self):
        """Test validate_vector with valid vectors."""
        vec = np.random.randn(768)
        validate_vector(vec, "param")
        validate_vector(vec, "param", expected_dim=768)
    
    def test_validate_vector_wrong_dim(self):
        """Test validate_vector with wrong dimension."""
        vec = np.random.randn(768)
        with pytest.raises(InvalidShapeError):
            validate_vector(vec, "param", expected_dim=512)


class TestListValidators:
    """Test list validation functions."""
    
    def test_validate_list_of_strings_success(self):
        """Test validate_list_of_strings with valid lists."""
        validate_list_of_strings(["a", "b", "c"], "param")
        validate_list_of_strings([], "param")  # Empty list is valid for type check
    
    def test_validate_list_of_strings_wrong_type(self):
        """Test validate_list_of_strings with non-strings."""
        with pytest.raises(InvalidParameterError):
            validate_list_of_strings([1, 2, 3], "param")
        
        with pytest.raises(InvalidParameterError):
            validate_list_of_strings(["a", 1, "c"], "param")
    
    def test_validate_list_not_empty_success(self):
        """Test validate_list_not_empty with valid lists."""
        validate_list_not_empty([1, 2, 3], "param")
        validate_list_not_empty(["a"], "param")
    
    def test_validate_list_not_empty_empty(self):
        """Test validate_list_not_empty with empty list."""
        with pytest.raises(EmptyInputError):
            validate_list_not_empty([], "param")
    
    def test_validate_list_not_empty_with_none(self):
        """Test validate_list_not_empty with None elements."""
        with pytest.raises(InvalidParameterError):
            validate_list_not_empty([1, None, 3], "param")


class TestBoundsValidators:
    """Test bounds validation functions."""
    
    def test_validate_index_bounds_success(self):
        """Test validate_index_bounds with valid indices."""
        validate_index_bounds(0, "idx", 10)
        validate_index_bounds(5, "idx", 10)
        validate_index_bounds(9, "idx", 10)
    
    def test_validate_index_bounds_negative(self):
        """Test validate_index_bounds with negative index."""
        with pytest.raises(InvalidParameterError):
            validate_index_bounds(-1, "idx", 10)
    
    def test_validate_index_bounds_too_large(self):
        """Test validate_index_bounds with out-of-bounds index."""
        with pytest.raises(InvalidParameterError):
            validate_index_bounds(10, "idx", 10)
    
    def test_validate_k_value_success(self):
        """Test validate_k_value with valid values."""
        validate_k_value(1, "k")
        validate_k_value(10, "k")
        validate_k_value(5, "k", max_k=10)
    
    def test_validate_k_value_zero(self):
        """Test validate_k_value with zero."""
        with pytest.raises(InvalidParameterError):
            validate_k_value(0, "k")
    
    def test_validate_k_value_exceeds_max(self):
        """Test validate_k_value with value exceeding max."""
        with pytest.raises(InvalidParameterError):
            validate_k_value(20, "k", max_k=10)


class TestTypeValidators:
    """Test type validation functions."""
    
    def test_validate_type_success(self):
        """Test validate_type with correct types."""
        validate_type("hello", "param", str)
        validate_type(123, "param", int)
        validate_type(1.5, "param", float)
        validate_type([1, 2], "param", list)
    
    def test_validate_type_failure(self):
        """Test validate_type with wrong types."""
        with pytest.raises(InvalidParameterError):
            validate_type("hello", "param", int)
        
        with pytest.raises(InvalidParameterError):
            validate_type(123, "param", str)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_validate_very_large_string(self):
        """Test validation with very large string."""
        large_str = "x" * 100000
        validate_not_empty(large_str, "param")
        
        with pytest.raises(InputTooLargeError):
            validate_max_length(large_str, "param", 10000)
    
    def test_validate_unicode_strings(self):
        """Test validation with Unicode strings."""
        validate_not_empty("你好世界", "param")
        validate_list_of_strings(["hello", "世界", "🌍"], "param")
    
    def test_validate_extreme_numeric_values(self):
        """Test validation with extreme numeric values."""
        validate_positive_int(2**31 - 1, "param")
        validate_positive_float(1e10, "param")
        validate_range(0.0001, "param", 0.0, 1.0)
    
    def test_validate_zero_size_arrays(self):
        """Test validation with zero-size arrays."""
        arr = np.array([]).reshape(0, 768)
        with pytest.raises(EmptyInputError):
            validate_2d_array(arr, "param")
        
        arr = np.array([]).reshape(10, 0)
        with pytest.raises(InvalidShapeError):
            validate_array_shape(arr, "param", 2, (-1, 768))
