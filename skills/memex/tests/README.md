# Memex Test Suite

Comprehensive test coverage for the Memex AI Second Brain system.

## Overview

This test suite provides complete coverage for:

- **Plaud Scraper** - Authentication, transcript fetching, downloads, rate limiting
- **Vector Store** - Embeddings, search, recency scoring, context windows
- **Integration Tests** - Full workflow testing (requires credentials)

## Running Tests

### Run All Tests (Skip Integration)

```bash
pytest -v -m "not integration"
```

### Run Specific Test Files

```bash
# Test Plaud scraper only
pytest test_plaud_scraper.py -v

# Test vector store only
pytest test_vector_store.py -v
```

### Run Tests by Category

```bash
# Run only authentication tests
pytest test_plaud_scraper.py::TestPlaudScraperAuthentication -v

# Run only search tests
pytest test_vector_store.py::TestVectorStoreSearch -v
```

### Run Integration Tests (Requires Credentials)

```bash
# WARNING: This will make real API calls
pytest -v -m integration

# Run specific integration test
pytest test_plaud_scraper.py::TestPlaudScraperIntegration -v -m integration
```

### Run with Coverage

```bash
# Install coverage first
pip install pytest-cov

# Run with coverage report
pytest --cov=../memex --cov-report=html --cov-report=term -v
```

## Test Structure

```
tests/
├── __init__.py              # Test suite initialization
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini               # Pytest configuration
├── test_plaud_scraper.py    # Plaud scraper test suite
├── test_vector_store.py     # Vector store test suite
└── README.md                # This file
```

## Test Categories

### 1. Plaud Scraper Tests

**Authentication Tests** (`TestPlaudScraperAuthentication`)

- Login success/failure
- 2FA handling
- Session persistence

**Transcript List Tests** (`TestPlaudScraperTranscriptList`)

- Basic fetching
- Pagination
- Empty results

**Download Tests** (`TestPlaudScraperDownload`)

- JSON/TXT format downloads
- Retry logic on failure
- Error handling

**Batch Export Tests** (`TestPlaudScraperBatchExport`)

- Basic batch processing
- Incremental updates
- Progress callbacks

**Rate Limiting Tests** (`TestPlaudScraperRateLimiting`)

- Rate limit enforcement
- Backoff strategies

**Error Handling Tests** (`TestPlaudScraperErrorHandling`)

- Session expiry
- Network errors
- Partial failures

### 2. Vector Store Tests

**Embedding Tests** (`TestVectorStoreEmbeddings`)

- Dimension validation
- Determinism
- Batch efficiency

**Add Content Tests** (`TestVectorStoreAddContent`)

- Transcript ingestion
- Journal entry storage
- Duplicate handling

**Search Tests** (`TestVectorStoreSearch`)

- Basic semantic search
- Recency weighting
- Cross-collection search
- Metadata filtering

**Recency Scoring Tests** (`TestVectorStoreRecencyScoring`)

- Score calculation
- Date handling
- Edge cases

**Context Window Tests** (`TestVectorStoreContextWindow`)

- Token limit enforcement
- Formatting
- Metadata inclusion

**Performance Tests** (`TestVectorStorePerformance`)

- Bulk insert performance
- Query performance at scale

**Integration Tests** (`TestVectorStoreIntegration`)

- Full workflow testing

## Fixtures

### Temporary Directories

- `temp_dir` - Clean temporary directory
- `data_dir` - Structured data directory

### Sample Data

- `sample_transcript` - Full transcript text
- `sample_transcript_segments` - Segmented transcript
- `sample_metadata` - Recording metadata
- `sample_journal_entry` - Journal entry data

### Mock Objects

- `mock_playwright_page` - Mock browser page
- `mock_playwright_browser` - Mock browser instance
- `mock_chroma_collection` - Mock ChromaDB collection

### Utilities

- `generate_transcript_batch` - Generate multiple transcripts
- `generate_journal_batch` - Generate multiple journals
- `assert_valid_embedding` - Validate embedding structure
- `assert_valid_metadata` - Validate metadata structure

## Test Isolation

All tests are isolated using:

- Temporary directories (cleaned up after each test)
- Mock objects (no external dependencies)
- Fixtures (reproducible test data)

## Continuous Integration

To run in CI/CD:

```bash
# Install dependencies
pip install -r requirements-test.txt

# Run tests with coverage
pytest --cov=../memex --cov-report=xml -v -m "not integration"
```

## Writing New Tests

### Test File Template

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestMyFeature:
    """Test suite for my feature."""

    @pytest.fixture
    def my_fixture(self, tmp_path):
        """Setup fixture for tests."""
        # Setup code
        yield fixture_value
        # Cleanup code

    def test_basic_functionality(self, my_fixture):
        """Test basic functionality."""
        # Arrange
        input_data = ...

        # Act
        result = my_feature.process(input_data)

        # Assert
        assert result == expected_output
```

### Async Test Template

```python
@pytest.mark.asyncio
async def test_async_feature(self, my_fixture):
    """Test async functionality."""
    result = await my_async_function()
    assert result is not None
```

## Debugging Tests

### Run Single Test with Print Statements

```bash
pytest test_plaud_scraper.py::TestPlaudScraperAuthentication::test_login_success -v -s
```

### Run with PDB Debugger

```bash
pytest test_plaud_scraper.py -v --pdb
```

### Increase Logging Verbosity

```bash
pytest test_vector_store.py -v --log-cli-level=DEBUG
```

## Best Practices

1. **Test Behavior, Not Implementation** - Focus on what the code should do, not how
2. **Arrange-Act-Assert Pattern** - Clear test structure
3. **Descriptive Test Names** - Use `test_<what>_<when>_<expected>`
4. **Independent Tests** - No test should depend on another
5. **Fast Feedback** - Keep unit tests fast; mark slow tests appropriately
6. **Mock External Dependencies** - Don't make real API calls in unit tests
7. **Use Fixtures** - DRY principle for test data

## Requirements

```bash
# Core testing
pytest>=7.0.0
pytest-asyncio>=0.21.0

# Mocking
pytest-mock>=3.10.0

# Coverage (optional)
pytest-cov>=4.0.0

# Additional
numpy>=1.24.0
```

## Troubleshooting

### Import Errors

```bash
# Add parent directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/Users/arvindsarin/Cursor/Claude-2026/clawd/memex"
```

### Async Tests Failing

Make sure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio
```

### ChromaDB Errors

Ensure ChromaDB is installed:

```bash
pip install chromadb
```

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure all tests pass: `pytest -v`
3. Check coverage: `pytest --cov=../memex`
4. Update this README if needed

## License

Part of the Memex AI Second Brain project.
