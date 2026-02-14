# Memex Testing Patterns & Best Practices

Quick reference guide for common testing patterns used in the Memex test suite.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Async Testing](#async-testing)
3. [Mocking Patterns](#mocking-patterns)
4. [Fixture Patterns](#fixture-patterns)
5. [Assertion Patterns](#assertion-patterns)
6. [Error Testing](#error-testing)
7. [Performance Testing](#performance-testing)

---

## Test Structure

### Arrange-Act-Assert (AAA) Pattern

```python
def test_example(self, fixture):
    """Test description following behavior pattern."""
    # ARRANGE - Set up test data and preconditions
    input_data = {"key": "value"}
    expected_output = "processed_value"

    # ACT - Execute the code under test
    result = my_function(input_data)

    # ASSERT - Verify the outcome
    assert result == expected_output
```

### Class-Based Organization

```python
class TestFeatureName:
    """Test suite for specific feature."""

    @pytest.fixture
    def feature_setup(self):
        """Setup specific to this feature."""
        return FeatureObject()

    def test_basic_functionality(self, feature_setup):
        """Test the basic happy path."""
        pass

    def test_edge_case(self, feature_setup):
        """Test specific edge case."""
        pass

    def test_error_handling(self, feature_setup):
        """Test error scenarios."""
        pass
```

---

## Async Testing

### Basic Async Test

```python
@pytest.mark.asyncio
async def test_async_function(self):
    """Test async functionality."""
    result = await my_async_function()
    assert result is not None
```

### Async Fixture

```python
@pytest.fixture
async def async_resource(self):
    """Create async resource for testing."""
    resource = await create_resource()
    yield resource
    await cleanup_resource(resource)
```

### Mock Async Functions

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_with_async_mock(self):
    """Test using async mocks."""
    mock_service = AsyncMock()
    mock_service.fetch_data.return_value = {"data": "value"}

    result = await my_function(mock_service)

    assert mock_service.fetch_data.called
    assert result == {"data": "value"}
```

---

## Mocking Patterns

### Mock Object Creation

```python
from unittest.mock import Mock, AsyncMock, patch

# Simple mock
mock_obj = Mock()
mock_obj.method.return_value = "value"

# Async mock
async_mock = AsyncMock()
async_mock.method.return_value = "value"

# Mock with spec (validates method calls)
mock_obj = Mock(spec=RealClass)
```

### Patching

```python
# Patch function in module
@patch('module.function_name')
def test_with_patch(mock_func):
    mock_func.return_value = "mocked"
    result = call_function_that_uses_function_name()
    assert result == "mocked"

# Patch object method
with patch.object(obj, 'method_name') as mock_method:
    mock_method.return_value = "mocked"
    result = obj.method_name()
    assert result == "mocked"

# Patch class
@patch('module.ClassName')
def test_with_class_patch(MockClass):
    instance = MockClass.return_value
    instance.method.return_value = "mocked"
```

### Side Effects

```python
# Exception on call
mock_obj.method.side_effect = ValueError("Error message")

# Different returns per call
mock_obj.method.side_effect = [1, 2, 3]

# Custom function
def custom_behavior(*args, **kwargs):
    return f"Called with {args}"

mock_obj.method.side_effect = custom_behavior
```

### Verify Mock Calls

```python
# Check if called
assert mock_obj.method.called
assert mock_obj.method.call_count == 3

# Check call arguments
mock_obj.method.assert_called_once_with(arg1, arg2)
mock_obj.method.assert_called_with(arg1, arg2)

# Get call arguments
args, kwargs = mock_obj.method.call_args
all_calls = mock_obj.method.call_args_list
```

---

## Fixture Patterns

### Simple Fixture

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"id": 1, "name": "test"}
```

### Fixture with Setup/Teardown

```python
@pytest.fixture
def temp_file(tmp_path):
    """Create temporary file for testing."""
    # Setup
    file_path = tmp_path / "test.txt"
    file_path.write_text("content")

    yield file_path

    # Teardown (optional, tmp_path auto-cleans)
    if file_path.exists():
        file_path.unlink()
```

### Fixture Factory

```python
@pytest.fixture
def make_user():
    """Factory for creating test users."""
    def _make_user(name="default", email="test@example.com"):
        return User(name=name, email=email)
    return _make_user

# Usage
def test_users(make_user):
    user1 = make_user(name="Alice")
    user2 = make_user(name="Bob")
```

### Parameterized Fixture

```python
@pytest.fixture(params=[1, 2, 3])
def number(request):
    """Test with multiple values."""
    return request.param

def test_with_params(number):
    """Runs 3 times with different values."""
    assert number > 0
```

### Scope Fixtures

```python
# Function scope (default) - new instance per test
@pytest.fixture(scope="function")
def func_fixture():
    return Resource()

# Class scope - shared within test class
@pytest.fixture(scope="class")
def class_fixture():
    return Resource()

# Module scope - shared within module
@pytest.fixture(scope="module")
def module_fixture():
    return Resource()

# Session scope - shared across entire test session
@pytest.fixture(scope="session")
def session_fixture():
    return Resource()
```

---

## Assertion Patterns

### Basic Assertions

```python
# Equality
assert result == expected
assert result != unexpected

# Identity
assert result is None
assert result is not None

# Membership
assert item in collection
assert item not in collection

# Type checking
assert isinstance(result, ExpectedType)

# Boolean
assert condition
assert not condition
```

### Collection Assertions

```python
# Length
assert len(collection) == 5
assert len(collection) > 0

# All/Any
assert all(x > 0 for x in numbers)
assert any(x > 10 for x in numbers)

# Set operations
assert set(result) == set(expected)
assert set(result).issubset(set(expected))
```

### Numeric Assertions

```python
# Approximate equality
assert abs(result - expected) < 0.01

# Range checking
assert 0.35 < score < 0.40

# NumPy arrays
import numpy as np
np.testing.assert_array_almost_equal(arr1, arr2)
np.testing.assert_array_equal(arr1, arr2)
```

### String Assertions

```python
# Containment
assert "substring" in text
assert text.startswith("prefix")
assert text.endswith("suffix")

# Case insensitive
assert "hello" in text.lower()

# Regex
import re
assert re.search(r"pattern", text)
```

### Custom Assertions

```python
def assert_valid_email(email):
    """Custom assertion for email validation."""
    assert "@" in email, f"Invalid email: {email}"
    assert "." in email.split("@")[1], f"Invalid domain: {email}"

# Usage
assert_valid_email("test@example.com")
```

---

## Error Testing

### Expected Exceptions

```python
# Basic exception check
with pytest.raises(ValueError):
    function_that_raises()

# Check exception message
with pytest.raises(ValueError, match="Invalid input"):
    function_that_raises()

# Store exception for inspection
with pytest.raises(ValueError) as exc_info:
    function_that_raises()

assert "Invalid" in str(exc_info.value)
```

### No Exception Raised

```python
# Ensure no exception
try:
    result = function_that_should_not_raise()
    assert result is not None
except Exception as e:
    pytest.fail(f"Unexpected exception: {e}")
```

### Retry Logic Testing

```python
def test_retry_on_failure(self):
    """Test retry behavior on transient errors."""
    attempts = []

    def mock_function(*args, **kwargs):
        attempts.append(1)
        if len(attempts) < 3:
            raise NetworkError("Transient error")
        return "success"

    with patch('module.function', side_effect=mock_function):
        result = retry_wrapper(function)

    assert len(attempts) == 3
    assert result == "success"
```

---

## Performance Testing

### Execution Time

```python
import time

def test_performance(self):
    """Test that operation completes quickly."""
    start = time.time()

    result = expensive_operation()

    elapsed = time.time() - start
    assert elapsed < 1.0  # Should complete in under 1 second
```

### Benchmark Fixture

```python
@pytest.fixture
def measure_time():
    """Utility to measure execution time."""
    def _measure(func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return result, elapsed
    return _measure

def test_with_benchmark(measure_time):
    result, elapsed = measure_time(my_function, arg1, arg2)
    assert elapsed < 0.5
```

### Scalability Testing

```python
@pytest.mark.parametrize("size", [10, 100, 1000])
def test_scales_linearly(size):
    """Test performance scales with input size."""
    data = generate_data(size)

    start = time.time()
    result = process(data)
    elapsed = time.time() - start

    # Should scale linearly (within margin)
    expected_time = size * 0.001  # 1ms per item
    assert elapsed < expected_time * 2  # Allow 2x margin
```

---

## Common Test Scenarios

### Testing File Operations

```python
def test_file_creation(tmp_path):
    """Test file is created with correct content."""
    file_path = tmp_path / "test.txt"

    write_file(file_path, "content")

    assert file_path.exists()
    assert file_path.read_text() == "content"
```

### Testing Database Operations

```python
def test_database_insert(temp_db):
    """Test inserting record into database."""
    # Arrange
    record = {"id": 1, "name": "test"}

    # Act
    db.insert(record)

    # Assert
    result = db.get(1)
    assert result == record
```

### Testing API Calls

```python
@patch('requests.get')
def test_api_call(mock_get):
    """Test API call handling."""
    mock_get.return_value.json.return_value = {"data": "value"}
    mock_get.return_value.status_code = 200

    result = fetch_from_api("endpoint")

    assert result == {"data": "value"}
    mock_get.assert_called_once_with("endpoint")
```

### Testing Pagination

```python
def test_pagination(self):
    """Test paginated results."""
    # Mock API returning pages
    page1 = [{"id": i} for i in range(10)]
    page2 = [{"id": i} for i in range(10, 15)]
    page3 = []

    with patch('module.fetch_page') as mock_fetch:
        mock_fetch.side_effect = [page1, page2, page3]

        results = fetch_all_pages()

    assert len(results) == 15
    assert mock_fetch.call_count == 3
```

---

## Test Organization

### Test Naming Convention

```python
# Pattern: test_<what>_<when>_<expected>

def test_login_with_valid_credentials_succeeds(self):
    """Login succeeds when credentials are valid."""
    pass

def test_search_with_empty_query_returns_empty_list(self):
    """Search returns empty list when query is empty."""
    pass

def test_download_with_network_error_retries_three_times(self):
    """Download retries 3 times when network error occurs."""
    pass
```

### Test Markers

```python
# Mark slow tests
@pytest.mark.slow
def test_slow_operation(self):
    pass

# Mark integration tests
@pytest.mark.integration
def test_external_api(self):
    pass

# Mark async tests
@pytest.mark.asyncio
async def test_async_operation(self):
    pass

# Skip tests conditionally
@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_feature(self):
    pass

# Custom markers
@pytest.mark.database
def test_database_feature(self):
    pass
```

---

## Debugging Tests

### Print Debugging

```bash
# Show print statements
pytest test_file.py -v -s

# Show captured output
pytest test_file.py -v --capture=no
```

### PDB Debugger

```bash
# Break on failure
pytest test_file.py --pdb

# Break on first failure
pytest test_file.py -x --pdb
```

### Increase Verbosity

```bash
# Verbose output
pytest test_file.py -v

# Very verbose
pytest test_file.py -vv

# Show full diff
pytest test_file.py -vv --tb=long
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.9"
      - run: pip install -r requirements-test.txt
      - run: pytest tests/ -v -m "not integration" --junitxml=results.xml
      - uses: actions/upload-artifact@v2
        if: always()
        with:
          name: test-results
          path: results.xml
```

---

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Asyncio](https://pytest-asyncio.readthedocs.io/)
- [Python Mocking](https://docs.python.org/3/library/unittest.mock.html)
- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

---

**Last Updated:** February 3, 2026
**Author:** Nike (Claude Agent)
**Project:** Memex AI Second Brain
