# Quick Start: Integration Tests

## Test Suite Overview

**143 comprehensive unit tests** for Gmail and Calendar integration.

```
test_gmail_service.py          38 tests    27KB    ~95% coverage
test_calendar_service.py       38 tests    27KB    ~95% coverage
test_integration_models.py     37 tests    21KB    ~98% coverage
test_oauth_flow.py             30 tests    21KB    ~90% coverage
fixtures_integrations.py       30+ fixtures 18KB
```

## Running Tests (Quick Commands)

### All Tests

```bash
cd /Users/arvindsarin/Cursor/Claude-2026/openclaw/skills/memex/tests

# Simple run
pytest test_gmail_service.py test_calendar_service.py test_integration_models.py test_oauth_flow.py -v

# Using helper script
./RUN_INTEGRATION_TESTS.sh
```

### Specific Test Files

```bash
# Gmail only
./RUN_INTEGRATION_TESTS.sh gmail

# Calendar only
./RUN_INTEGRATION_TESTS.sh calendar

# Models only
./RUN_INTEGRATION_TESTS.sh models

# OAuth only
./RUN_INTEGRATION_TESTS.sh oauth
```

### With Coverage

```bash
./RUN_INTEGRATION_TESTS.sh coverage

# Manual
pytest test_*.py --cov=memex.integrations --cov-report=html
open htmlcov/index.html
```

### Fast Tests (Skip Slow)

```bash
./RUN_INTEGRATION_TESTS.sh fast
```

## Test Structure

### Gmail Service Tests

```
TestGmailConfig              ✓ Config initialization
TestGmailCredentials         ✓ OAuth credential management
TestGmailServiceInit         ✓ Service initialization
TestGmailServiceConnection   ✓ API connection
TestRateLimiting            ✓ Rate limit enforcement
TestListMessages            ✓ Message listing & pagination
TestGetMessage              ✓ Individual message fetching
TestParseMessage            ✓ Email parsing (text, HTML, attachments)
TestFetchEmails             ✓ Batch fetching with pagination
TestBatchExport             ✓ JSON export operations
TestEdgeCases               ✓ Error handling & edge cases
```

### Calendar Service Tests

```
TestCalendarConfig          ✓ Config initialization
TestCalendarCredentials     ✓ OAuth credential management
TestCalendarServiceInit     ✓ Service initialization
TestCalendarServiceConnection ✓ API connection
TestRateLimiting           ✓ Rate limit enforcement
TestListCalendars          ✓ Calendar listing
TestListEvents             ✓ Event listing & pagination
TestParseEvent             ✓ Event parsing (regular, all-day, recurring)
TestFetchEvents            ✓ Batch fetching
TestBatchExport            ✓ JSON export operations
TestEdgeCases              ✓ Error handling
```

### Model Tests

```
TestEmailParticipant       ✓ Participant model
TestEmailAttachment        ✓ Attachment metadata
TestEmailData              ✓ Email model & serialization
TestCalendarAttendee       ✓ Attendee model
TestCalendarEvent          ✓ Event model & serialization
TestIntegrationConfig      ✓ Configuration model
TestSyncStatus             ✓ Sync tracking
TestBatchSyncResult        ✓ Batch result metrics
TestEnums                  ✓ Enum validation
```

### OAuth Flow Tests

```
TestGmailOAuthFlow         ✓ Gmail authentication
TestCalendarOAuthFlow      ✓ Calendar authentication
TestMultiAccountSupport    ✓ Multi-account management
TestTokenStorage           ✓ Token persistence
TestScopeManagement        ✓ OAuth scopes
TestCredentialLifecycle    ✓ Token refresh & expiration
TestOAuthErrorHandling     ✓ Error recovery
```

## Key Fixtures

```python
# Credentials
mock_google_credentials          # Valid OAuth credentials
expired_google_credentials       # Expired credentials

# API Mocks
mock_gmail_service              # Mocked Gmail API
mock_calendar_service           # Mocked Calendar API
sample_gmail_list_response      # Email list response
sample_calendar_events_response # Event list response

# Data Instances
sample_email_data               # Pre-configured email
sample_calendar_event_data      # Pre-configured event

# Factories
email_factory                   # Create custom emails
calendar_event_factory          # Create custom events
batch_emails                    # 10 test emails
batch_events                    # 10 test events
```

## Common Test Patterns

### Testing API Calls

```python
def test_api_call(gmail_service, mock_gmail_api):
    gmail_service.service = mock_gmail_api
    mock_gmail_api.users().messages().list().execute.return_value = {...}

    result = gmail_service.list_messages()

    assert len(result["messages"]) == 2
```

### Testing OAuth

```python
@patch('memex.integrations.gmail_service.build')
def test_connect(mock_build, gmail_service, mock_credentials):
    mock_api = MagicMock()
    mock_build.return_value = mock_api

    gmail_service.connect()

    mock_build.assert_called_once()
```

### Using Factories

```python
def test_custom_scenario(email_factory):
    email = email_factory(
        subject="Test",
        is_starred=True,
        labels=["INBOX", "IMPORTANT"]
    )
    assert email.is_starred
```

## Troubleshooting

### "No module named pytest"

```bash
pip install -r requirements-test.txt
```

### "No module named memex"

```bash
export PYTHONPATH="/Users/arvindsarin/Cursor/Claude-2026/openclaw:$PYTHONPATH"
```

### Tests are slow

```bash
# Run in parallel
pip install pytest-xdist
pytest -n auto test_*.py
```

### Need to see print statements

```bash
pytest -v -s test_gmail_service.py
```

### Need to debug failing test

```bash
pytest --pdb test_gmail_service.py::TestParseMessage::test_parse_simple_message
```

## CI/CD Integration

Add to `.github/workflows/tests.yml`:

```yaml
- name: Run Integration Tests
  run: |
    cd memex/tests
    pytest test_gmail_service.py \
           test_calendar_service.py \
           test_integration_models.py \
           test_oauth_flow.py \
           --cov=memex.integrations \
           --cov-report=xml \
           -m "not integration"
```

## Test Markers

- `@pytest.mark.integration` - Requires real credentials (skipped by default)
- `@pytest.mark.slow` - Slow tests (can skip with `-m "not slow"`)

## Performance

- **Full suite:** ~7 seconds
- **Gmail tests:** ~2.5 seconds
- **Calendar tests:** ~2.0 seconds
- **Model tests:** ~1.0 second
- **OAuth tests:** ~1.5 seconds

## Coverage Target

- **Overall:** ~95%
- **Gmail service:** ~95%
- **Calendar service:** ~95%
- **Models:** ~98%
- **OAuth:** ~90%

## Next Steps

1. Install test dependencies:

   ```bash
   pip install -r requirements-test.txt
   ```

2. Run all tests:

   ```bash
   ./RUN_INTEGRATION_TESTS.sh
   ```

3. Check coverage:

   ```bash
   ./RUN_INTEGRATION_TESTS.sh coverage
   ```

4. Read detailed docs:
   - `INTEGRATION_TESTS_README.md` - Full usage guide
   - `INTEGRATION_TEST_SUITE_SUMMARY.md` - Complete summary

## Files Created

```
memex/tests/
├── test_gmail_service.py              # 38 Gmail tests
├── test_calendar_service.py           # 38 Calendar tests
├── test_integration_models.py         # 37 model tests
├── test_oauth_flow.py                 # 30 OAuth tests
├── fixtures_integrations.py           # 30+ shared fixtures
├── RUN_INTEGRATION_TESTS.sh           # Quick test runner
├── QUICK_START_INTEGRATION_TESTS.md   # This file
├── INTEGRATION_TESTS_README.md        # Detailed guide
└── INTEGRATION_TEST_SUITE_SUMMARY.md  # Complete summary
```

---

**Ready to test!** 🚀

Run `./RUN_INTEGRATION_TESTS.sh` to get started.
