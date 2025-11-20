# Code Analysis Report

**Date**: 2024
**Scope**: Core modules of longevity-rag project
**Purpose**: Identify areas for improvement in methods, efficiency, and code quality

---

## Executive Summary

This analysis covers the core RAG pipeline modules:
- `src/rag/core.py` (125 lines) - Main RAG orchestration
- `src/nlp/embeddings.py` (157 lines) - Embeddings interface
- `src/rag/vector_store.py` (100 lines) - FAISS vector store wrapper
- `src/rag/generator.py` (137 lines) - LLM generator interface

**Overall Assessment**: Code is functional and well-structured, but needs:
1. Enhanced input validation
2. Better error handling with custom exceptions
3. Boundary condition checks
4. Performance optimizations for large datasets
5. More comprehensive unit tests

---

## Module: src/rag/core.py

### LongevityRAG.__init__()

**Current State**:
- ✅ Good: Path resolution logic handles multiple .npz scenarios
- ✅ Good: Clear error messages when files missing
- ⚠️ Issue: No validation of k parameter type/range
- ⚠️ Issue: No check if metadata file is empty or malformed
- ⚠️ Issue: JSON decode errors silently ignored with `continue`

**Recommendations**:
1. Add input validation for k parameter (must be positive integer)
2. Validate metadata file has at least one valid entry
3. Log JSON decode errors instead of silently skipping
4. Add type hints for all parameters
5. Consider lazy loading of vector store (only load on first query)

**Priority**: 🟠 High

### LongevityRAG.query()

**Current State**:
- ✅ Good: Clear logic flow (embed → search → assemble → generate)
- ✅ Good: Deduplication of PMIDs
- ⚠️ Issue: No validation of question parameter (empty string, None, very long)
- ⚠️ Issue: No bounds checking on idx before accessing metadata
- ⚠️ Issue: Confidence calculation doesn't handle empty scores edge case well
- ⚠️ Issue: Hard-coded k=10 for chunk assembly (should be configurable)

**Recommendations**:
1. Add input validation for question (not empty, max length)
2. Add bounds checking: `if 0 <= idx < len(self.metadata)`
3. Handle edge case: `confidence = 0.0 if not scores else float(sum(scores) / len(scores))`
4. Make chunk assembly limit configurable (not hard-coded 10)
5. Add logging for query time, number of results
6. Consider caching frequent queries

**Priority**: 🔴 Critical

---

## Module: src/nlp/embeddings.py

### Embeddings.__init__()

**Current State**:
- ✅ Good: Graceful fallback from real → mock
- ✅ Good: Device auto-detection (GPU/CPU)
- ⚠️ Issue: No validation of batch_size (must be positive)
- ⚠️ Issue: No validation of dim (must be positive)
- ⚠️ Issue: Model loading failure catches generic Exception (too broad)

**Recommendations**:
1. Validate batch_size > 0 and batch_size <= reasonable max (e.g., 256)
2. Validate dim > 0 and dim <= reasonable max (e.g., 2048)
3. Use specific exceptions: `except (OSError, ValueError) as e` for model loading
4. Add timeout for model loading (can hang on network issues)
5. Log model download progress

**Priority**: 🟡 Medium

### Embeddings.encode()

**Current State**:
- ✅ Good: Simple dispatch to mock or real
- ⚠️ Issue: No validation of texts parameter (None, empty list, non-strings)
- ⚠️ Issue: No handling of extremely long texts (>512 tokens)

**Recommendations**:
1. Validate texts is not None and is list/iterable
2. Validate all elements are strings
3. Warn if text exceeds max_length (512 tokens)
4. Handle empty list gracefully (return empty list)
5. Add progress callback for large batches

**Priority**: 🟠 High

### Embeddings._encode_mock()

**Current State**:
- ✅ Good: Deterministic for testing
- ✅ Good: L2 normalization
- ⚠️ Issue: Hash collision possible (uses modulo)
- ⚠️ Issue: No handling of empty string

**Recommendations**:
1. Use better hash function (hashlib.sha256)
2. Handle empty string explicitly (return zero vector or specific pattern)
3. Document determinism in docstring

**Priority**: 🟢 Low

### Embeddings._encode_real()

**Current State**:
- ✅ Good: Batch processing
- ✅ Good: [CLS] token for sentence embedding
- ✅ Good: L2 normalization
- ⚠️ Issue: No handling of CUDA OOM errors
- ⚠️ Issue: Batch size not dynamically adjusted on OOM

**Recommendations**:
1. Catch torch.cuda.OutOfMemoryError and retry with smaller batch
2. Add memory profiling to log peak memory usage
3. Clear CUDA cache between large batches
4. Add option to return embeddings as numpy arrays directly (avoid list conversion)

**Priority**: 🟠 High

---

## Module: src/rag/vector_store.py

### FaissVectorStore.__init__()

**Current State**:
- ✅ Good: Dual mode (FAISS / numpy fallback)
- ✅ Good: L2 normalization
- ⚠️ Issue: No validation of embeddings shape (must be 2D)
- ⚠️ Issue: No check for empty embeddings array

**Recommendations**:
1. Validate embeddings.shape is 2D: `if embeddings.ndim != 2`
2. Validate embeddings not empty: `if embeddings.shape[0] == 0`
3. Validate dim > 0: `if embeddings.shape[1] == 0`
4. Add logging of index size and dimension

**Priority**: 🟠 High

### FaissVectorStore.search()

**Current State**:
- ✅ Good: Handles both FAISS and numpy paths
- ⚠️ Issue: No validation of k parameter (must be positive, <= index size)
- ⚠️ Issue: query_embedding shape not validated
- ⚠️ Issue: Division by zero possible in normalization

**Recommendations**:
1. Validate k > 0 and k <= len(self.embeddings)
2. Validate query_embedding shape matches index dimension
3. Use safer normalization: `q / (np.linalg.norm(q) + 1e-12)`
4. Handle edge case: empty index (return empty results)

**Priority**: 🔴 Critical

### FaissVectorStore.save() / load()

**Current State**:
- ✅ Good: Creates parent directories
- ✅ Good: Handles .npz extension variations
- ⚠️ Issue: No validation that save succeeded
- ⚠️ Issue: No checksum/integrity validation on load

**Recommendations**:
1. Verify file exists and size > 0 after save
2. Add checksum (e.g., MD5) to verify data integrity
3. Add version number to file format for future compatibility
4. Use atomic writes (temp file → rename)

**Priority**: 🟡 Medium

---

## Module: src/rag/generator.py

### LLMGenerator.__init__()

**Current State**:
- ✅ Good: Auto-fallback to mock if OpenAI unavailable
- ✅ Good: Reads API key from environment
- ⚠️ Issue: No validation of temperature (must be 0.0-1.0)
- ⚠️ Issue: No validation of max_tokens (must be positive)
- ⚠️ Issue: Model name not validated (could be invalid)

**Recommendations**:
1. Validate temperature: `if not 0.0 <= temperature <= 1.0`
2. Validate max_tokens > 0 and max_tokens <= model limit
3. Validate model name against known models list
4. Add retry logic for API initialization

**Priority**: 🟡 Medium

### LLMGenerator.generate()

**Current State**:
- ✅ Good: Delegates to provider-specific methods
- ⚠️ Issue: No validation of prompt (empty, None, too long)
- ⚠️ Issue: No rate limiting for API calls

**Recommendations**:
1. Validate prompt not empty
2. Validate prompt length < model context limit
3. Add rate limiting (e.g., max 10 requests/second)
4. Add caching for duplicate prompts
5. Log token usage for cost tracking

**Priority**: 🟠 High

### LLMGenerator._generate_openai()

**Current State**:
- ✅ Good: Proper error handling with try-except
- ✅ Good: System message sets context
- ⚠️ Issue: Generic Exception catch (should be more specific)
- ⚠️ Issue: No retry logic for transient errors (rate limit, network)
- ⚠️ Issue: No timeout configured

**Recommendations**:
1. Use specific exceptions: `except (openai.OpenAIError, TimeoutError) as e`
2. Add retry with exponential backoff (3 retries, 2^n seconds)
3. Add timeout parameter (e.g., 30 seconds)
4. Log token usage from response
5. Handle rate limit errors gracefully

**Priority**: 🔴 Critical

---

## Common Issues Across Modules

### 1. Input Validation
**Issue**: Most methods lack comprehensive input validation
**Impact**: Can crash or produce incorrect results on invalid input
**Recommendation**: Add validation decorators or helper functions

### 2. Error Handling
**Issue**: Generic exceptions used, silent failures, no custom exception hierarchy
**Impact**: Difficult to debug, poor user experience
**Recommendation**: Create custom exception classes, log all errors

### 3. Logging
**Issue**: Inconsistent logging, missing important events
**Impact**: Difficult to debug production issues
**Recommendation**: Add structured logging with consistent format

### 4. Testing
**Issue**: Missing tests for edge cases and error conditions
**Impact**: Bugs not caught until production
**Recommendation**: Add comprehensive test suite with >80% coverage

### 5. Performance
**Issue**: No profiling, potential bottlenecks in batch processing
**Impact**: Slow on large datasets
**Recommendation**: Add profiling, optimize hot paths

---

## Action Items Summary

### Critical Priority 🔴
1. Add input validation to `LongevityRAG.query()` (question, k)
2. Add bounds checking in `LongevityRAG.query()` for metadata access
3. Add input validation to `FaissVectorStore.search()` (k, query shape)
4. Add retry logic to `LLMGenerator._generate_openai()`

### High Priority 🟠
1. Add validation to `Embeddings.encode()` (texts parameter)
2. Add OOM handling to `Embeddings._encode_real()`
3. Add validation to `FaissVectorStore.__init__()` (embeddings shape)
4. Add validation to `LLMGenerator.generate()` (prompt)

### Medium Priority 🟡
1. Add validation to `Embeddings.__init__()` (batch_size, dim)
2. Add integrity checks to `FaissVectorStore.save()/load()`
3. Add validation to `LLMGenerator.__init__()` (temperature, max_tokens)

### Low Priority 🟢
1. Improve hash function in `Embeddings._encode_mock()`
2. Add caching to `LongevityRAG.query()`
3. Add progress callbacks for long operations

---

## Next Steps

1. **Create custom exception hierarchy** (`src/utils/errors.py`)
2. **Create validation utilities** (`src/utils/validation.py`)
3. **Refactor core.py** with input validation and better error handling
4. **Add comprehensive unit tests** for all edge cases
5. **Profile performance** and optimize bottlenecks

