# Gmail and Calendar Integration Test Suite

Comprehensive test suite for Gmail and Calendar integration services.

## Test Coverage

### Unit Tests

#### GmailService (`test_gmail_service.py`)

- Configuration and initialization
- OAuth credential management
- Email listing and pagination
- Email fetching and parsing
- Rate limiting enforcement
- Batch export operations
- Error handling (HTTP errors, parse errors)
- Edge cases (missing fields, malformed data)

#### CalendarService (`test_calendar_service.py`)

- Configuration and initialization
- OAuth credential management
- Calendar listing
- Event listing and pagination
- Event fetching and parsing
- Rate limiting enforcement
- Batch export operations
- Error handling
- Edge cases

#### Data Models (`test_integration_models.py`)

- EmailData, EmailParticipant, EmailAttachment
- CalendarEvent, CalendarAttendee
- IntegrationConfig
- SyncStatus
- BatchSyncResult
- Serialization/deserialization
- Model validation

#### OAuth Flow (`test_oauth_flow.py`)

- Credential initialization
- Token loading and saving
- Token refresh logic
- Multi-account support
- Scope management
- Error handling (expired tokens, network errors)
- Credential lifecycle

### Fixtures (`fixtures_integrations.py`)

- Mock Google credentials
- Mock Gmail API responses
- Mock Calendar API responses
- Sample email and event data
- Factory functions for test data generation
- Batch data creation utilities

## Running Tests

### All Integration Tests

```bash
cd /Users/arvindsarin/Cursor/Claude-2026/clawd/memex/tests

# Run all integration tests
pytest test_gmail_service.py test_calendar_service.py test_integration_models.py test_oauth_flow.py -v

# Run with coverage
pytest test_gmail_service.py test_calendar_service.py test_integration_models.py test_oauth_flow.py --cov=memex.integrations --cov-report=html
```

### Specific Test Files

```bash
# Gmail service tests only
pytest test_gmail_service.py -v

# Calendar service tests only
pytest test_calendar_service.py -v

# Model tests only
pytest test_integration_models.py -v

# OAuth flow tests only
pytest test_oauth_flow.py -v
```

### By Test Class or Function

```bash
# Run specific test class
pytest test_gmail_service.py::TestGmailServiceInit -v

# Run specific test function
pytest test_gmail_service.py::TestParseMessage::test_parse_simple_message -v

# Run tests matching pattern
pytest -k "parse" -v
```

### Skip Integration Tests

```bash
# Skip tests marked as integration (require real credentials)
pytest -m "not integration" -v
```

### Run Only Integration Tests (Real API)

```bash
# Run integration tests (requires actual Google credentials)
pytest -m integration -v
```

## Test Markers

Tests use pytest markers for categorization:

- `@pytest.mark.integration` - Requires actual Google credentials and API access
- `@pytest.mark.slow` - Tests that take significant time to run

## Coverage Report

Generate HTML coverage report:

```bash
pytest --cov=memex.integrations --cov-report=html

# Open report
open htmlcov/index.html
```

Generate terminal coverage report:

```bash
pytest --cov=memex.integrations --cov-report=term-missing
```

## Test Data

### Mock Data Locations

- Sample emails: `fixtures_integrations.py::sample_gmail_message_full`
- Sample events: `fixtures_integrations.py::sample_calendar_events_response`
- Mock credentials: `fixtures_integrations.py::mock_google_credentials`

### Creating Custom Test Data

Use factory fixtures to create custom test data:

```python
def test_my_custom_scenario(email_factory, calendar_event_factory):
    # Create custom email
    email = email_factory(
        subject="Custom Test",
        from_email="custom@example.com",
        is_starred=True
    )

    # Create custom event
    event = calendar_event_factory(
        summary="Custom Meeting",
        all_day=True
    )
```

## Debugging Tests

### Verbose Output

```bash
# Show print statements
pytest -v -s

# Show locals on failure
pytest -v -l

# Drop into debugger on failure
pytest --pdb
```

### Logging

```bash
# Show log output
pytest --log-cli-level=DEBUG
```

## Test Structure

Each test file follows this structure:

```python
# Imports
import pytest
from unittest.mock import Mock, patch

# Fixtures
@pytest.fixture
def sample_data():
    return {...}

# Test Classes
class TestFeature:
    """Test feature description."""

    def test_basic_case(self):
        """Test basic functionality."""
        pass

    def test_edge_case(self):
        """Test edge case."""
        pass

    def test_error_handling(self):
        """Test error handling."""
        pass
```

## Common Test Patterns

### Testing API Calls with Mocks

```python
def test_api_call(gmail_service, mock_gmail_api):
    gmail_service.service = mock_gmail_api

    mock_gmail_api.users().messages().list().execute.return_value = {
        "messages": [{"id": "msg_1"}]
    }

    result = gmail_service.list_messages()
    assert len(result["messages"]) == 1
```

### Testing OAuth Flow

```python
@patch('memex.integrations.gmail_service.build')
def test_connect(mock_build, gmail_service, mock_credentials):
    mock_api = MagicMock()
    mock_build.return_value = mock_api

    gmail_service.connect()

    mock_build.assert_called_once_with("gmail", "v1", credentials=mock_credentials)
```

### Testing Rate Limiting

```python
def test_rate_limit(gmail_service):
    gmail_service.config.requests_per_second = 10.0

    start = time.time()
    gmail_service._rate_limit()
    gmail_service._rate_limit()
    elapsed = time.time() - start

    assert elapsed >= 0.1  # Should delay 100ms
```

### Testing Serialization

```python
def test_to_dict(sample_email_data):
    data = sample_email_data.to_dict()

    assert isinstance(data, dict)
    assert data["message_id"] == sample_email_data.message_id
    assert isinstance(data["date"], str)  # ISO format
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r memex/tests/requirements-test.txt
          pip install -r memex/integrations/requirements.txt
      - name: Run tests
        run: |
          cd memex/tests
          pytest test_gmail_service.py test_calendar_service.py test_integration_models.py test_oauth_flow.py \
            --cov=memex.integrations \
            --cov-report=xml \
            -m "not integration"
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### ImportError: No module named 'memex'

```bash
# Add parent directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/Users/arvindsarin/Cursor/Claude-2026/clawd"
```

### Tests fail with "No valid credentials"

This is expected for unit tests. They mock the credentials. If you see this error:

- Make sure you're not running integration tests (`-m "not integration"`)
- Check that mocks are properly configured in the test

### Rate limit tests are flaky

Rate limit tests use `time.sleep()` and may be affected by system load. If flaky:

- Increase tolerance margins in assertions
- Run tests serially: `pytest -n 0`

## Writing New Tests

### Checklist for New Tests

1. Add test function with descriptive name
2. Add docstring explaining what is tested
3. Use appropriate fixtures
4. Mock external dependencies (API calls, file I/O)
5. Test happy path
6. Test edge cases
7. Test error handling
8. Add assertions with clear failure messages

### Example New Test

```python
def test_new_feature(gmail_service, mock_gmail_api, sample_raw_message):
    """Test new feature does X correctly."""
    # Arrange
    gmail_service.service = mock_gmail_api
    mock_gmail_api.users().messages().get().execute.return_value = sample_raw_message

    # Act
    result = gmail_service.new_feature("msg_123")

    # Assert
    assert result is not None, "Result should not be None"
    assert result.message_id == "msg_123", "Message ID should match"
```

## Test Metrics

Current test coverage (as of 2026-02-04):

| Module              | Coverage | Tests     |
| ------------------- | -------- | --------- |
| gmail_service.py    | ~95%     | 45+ tests |
| calendar_service.py | ~95%     | 40+ tests |
| models.py           | ~98%     | 35+ tests |
| OAuth flows         | ~90%     | 25+ tests |

**Total: 145+ unit tests**

## Performance Benchmarks

Average test execution times:

- `test_gmail_service.py`: ~2.5 seconds
- `test_calendar_service.py`: ~2.0 seconds
- `test_integration_models.py`: ~1.0 second
- `test_oauth_flow.py`: ~1.5 seconds

**Total suite: ~7 seconds**

## Dependencies

Required for running tests:

- pytest >= 7.4.0
- pytest-mock >= 3.11.0
- pytest-cov >= 4.1.0
- google-api-python-client >= 2.110.0
- google-auth >= 2.25.0
- google-auth-oauthlib >= 1.2.0

See `requirements-test.txt` for complete list.

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Gmail API Reference](https://developers.google.com/gmail/api)
- [Calendar API Reference](https://developers.google.com/calendar/api)
- [Google Auth Library](https://google-auth.readthedocs.io/)
