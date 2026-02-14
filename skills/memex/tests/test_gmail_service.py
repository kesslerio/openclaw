"""
Unit tests for GmailService.

Tests cover:
- Service initialization and configuration
- OAuth credential management
- Email fetching and parsing
- Rate limiting
- Batch export operations
- Error handling
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

from memex.integrations.gmail_service import (
    GmailService,
    GmailConfig,
    GmailCredentials,
)
from memex.integrations.models import (
    EmailData,
    EmailParticipant,
    EmailAttachment,
    IntegrationType,
)


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def gmail_config(temp_dir):
    """Gmail configuration for testing."""
    return GmailConfig(
        credentials_path=str(temp_dir / "credentials.json"),
        token_dir=str(temp_dir / ".tokens"),
        requests_per_second=10.0,  # Faster for tests
    )


@pytest.fixture
def mock_credentials():
    """Mock Google OAuth2 credentials."""
    creds = Mock(spec=Credentials)
    creds.valid = True
    creds.expired = False
    creds.refresh_token = "mock_refresh_token"
    creds.token = "mock_access_token"
    creds.to_json.return_value = json.dumps({
        "token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
    })
    return creds


@pytest.fixture
def gmail_service(gmail_config, mock_credentials):
    """GmailService instance with mocked credentials."""
    service = GmailService(config=gmail_config, account_email="test@example.com")

    # Mock the credentials manager
    service.credentials_manager.credentials = mock_credentials
    service.credentials_manager.get_credentials = Mock(return_value=mock_credentials)

    return service


@pytest.fixture
def mock_gmail_api():
    """Mock Gmail API service."""
    api = MagicMock()

    # Mock the users().messages() chain
    messages_api = MagicMock()
    api.users.return_value.messages.return_value = messages_api

    return api


@pytest.fixture
def sample_raw_message():
    """Sample raw Gmail API message."""
    return {
        "id": "msg_12345",
        "threadId": "thread_67890",
        "labelIds": ["INBOX", "UNREAD"],
        "payload": {
            "mimeType": "text/plain",
            "headers": [
                {"name": "From", "value": "Alice Johnson <alice@example.com>"},
                {"name": "To", "value": "bob@example.com"},
                {"name": "Cc", "value": "charlie@example.com"},
                {"name": "Subject", "value": "Project Update"},
                {"name": "Date", "value": "Mon, 03 Feb 2026 10:30:00 -0800"},
            ],
            "body": {
                "data": "SGVsbG8gV29ybGQh"  # Base64 for "Hello World!"
            }
        }
    }


@pytest.fixture
def sample_multipart_message():
    """Sample multipart email with HTML and attachments."""
    return {
        "id": "msg_99999",
        "threadId": "thread_88888",
        "labelIds": ["INBOX", "STARRED"],
        "payload": {
            "mimeType": "multipart/mixed",
            "headers": [
                {"name": "From", "value": "sender@example.com"},
                {"name": "To", "value": "recipient@example.com"},
                {"name": "Subject", "value": "Report with Attachment"},
                {"name": "Date", "value": "Tue, 04 Feb 2026 14:00:00 -0800"},
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": "UGxhaW4gdGV4dCBib2R5"}  # "Plain text body"
                },
                {
                    "mimeType": "text/html",
                    "body": {"data": "PGI+SFRNTCBib2R5PC9iPg=="}  # "<b>HTML body</b>"
                },
                {
                    "mimeType": "application/pdf",
                    "filename": "report.pdf",
                    "body": {
                        "attachmentId": "att_12345",
                        "size": 51200
                    }
                }
            ]
        }
    }


# ============================================================
# GmailConfig Tests
# ============================================================


class TestGmailConfig:
    """Test GmailConfig initialization and defaults."""

    def test_default_config(self):
        """Test default configuration values."""
        config = GmailConfig()

        assert config.credentials_path == "credentials.json"
        assert config.token_dir == ".tokens"
        assert config.requests_per_second == 5.0
        assert "https://www.googleapis.com/auth/gmail.readonly" in config.scopes

    def test_custom_config(self):
        """Test custom configuration values."""
        config = GmailConfig(
            credentials_path="/custom/creds.json",
            token_dir="/custom/tokens",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            requests_per_second=10.0
        )

        assert config.credentials_path == "/custom/creds.json"
        assert config.token_dir == "/custom/tokens"
        assert config.requests_per_second == 10.0
        assert len(config.scopes) == 1


# ============================================================
# GmailCredentials Tests
# ============================================================


class TestGmailCredentials:
    """Test OAuth credential management."""

    def test_initialization(self, gmail_config):
        """Test credentials manager initialization."""
        creds_manager = GmailCredentials(gmail_config, "test@example.com")

        assert creds_manager.account_email == "test@example.com"
        assert creds_manager.config == gmail_config
        assert "gmail_test@example.com.json" in str(creds_manager.token_path)

    def test_get_credentials_valid(self, gmail_config, mock_credentials):
        """Test getting valid credentials."""
        creds_manager = GmailCredentials(gmail_config, "test@example.com")
        creds_manager.credentials = mock_credentials

        result = creds_manager.get_credentials()

        assert result == mock_credentials
        assert result.valid

    def test_get_credentials_refresh_needed(self, gmail_config, temp_dir):
        """Test refreshing expired credentials."""
        creds_manager = GmailCredentials(gmail_config, "test@example.com")

        # Create expired credentials
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"
        mock_creds.refresh = Mock()
        mock_creds.to_json.return_value = "{}"

        creds_manager.credentials = mock_creds

        # Should refresh
        with patch.object(creds_manager.credentials, 'refresh') as mock_refresh:
            # Make credentials valid after refresh
            mock_creds.valid = True
            result = creds_manager.get_credentials()

            mock_refresh.assert_called_once()

    def test_get_credentials_missing_raises_error(self, gmail_config):
        """Test that missing credentials raises ValueError."""
        creds_manager = GmailCredentials(gmail_config, "test@example.com")

        with pytest.raises(ValueError, match="No valid credentials"):
            creds_manager.get_credentials()

    def test_save_credentials(self, gmail_config, mock_credentials, temp_dir):
        """Test saving credentials to file."""
        creds_manager = GmailCredentials(gmail_config, "test@example.com")
        creds_manager.credentials = mock_credentials

        creds_manager._save_credentials()

        assert creds_manager.token_path.exists()
        assert creds_manager.token_path.parent.exists()


# ============================================================
# GmailService Initialization Tests
# ============================================================


class TestGmailServiceInit:
    """Test GmailService initialization."""

    def test_init_with_config(self, gmail_config):
        """Test initialization with custom config."""
        service = GmailService(config=gmail_config, account_email="test@example.com")

        assert service.config == gmail_config
        assert service.account_email == "test@example.com"
        assert service.service is None
        assert service._last_request_time == 0.0

    def test_init_default_config(self):
        """Test initialization with default config."""
        service = GmailService(account_email="test@example.com")

        assert service.config is not None
        assert service.account_email == "test@example.com"


# ============================================================
# Connection and Authentication Tests
# ============================================================


class TestGmailServiceConnection:
    """Test Gmail API connection."""

    @patch('memex.integrations.gmail_service.build')
    def test_connect(self, mock_build, gmail_service, mock_credentials):
        """Test connecting to Gmail API."""
        mock_api = MagicMock()
        mock_build.return_value = mock_api

        gmail_service.connect()

        mock_build.assert_called_once_with("gmail", "v1", credentials=mock_credentials)
        assert gmail_service.service == mock_api

    @patch('memex.integrations.gmail_service.build')
    def test_authorize(self, mock_build, gmail_service, mock_credentials):
        """Test authorization flow."""
        mock_api = MagicMock()
        mock_build.return_value = mock_api

        # Mock authorize to avoid actual OAuth flow
        gmail_service.credentials_manager.authorize = Mock(return_value=mock_credentials)

        gmail_service.authorize()

        gmail_service.credentials_manager.authorize.assert_called_once()
        assert gmail_service.service == mock_api


# ============================================================
# Rate Limiting Tests
# ============================================================


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_enforced(self, gmail_service):
        """Test that rate limiting delays requests."""
        gmail_service.config.requests_per_second = 10.0  # 100ms between requests

        start_time = time.time()

        # First request - no delay
        gmail_service._rate_limit()

        # Second request - should be delayed
        gmail_service._rate_limit()

        elapsed = time.time() - start_time

        # Should take at least 100ms (0.1 seconds)
        assert elapsed >= 0.09  # Allow small margin

    def test_rate_limit_no_delay_when_enough_time_passed(self, gmail_service):
        """Test no delay when enough time has passed."""
        gmail_service.config.requests_per_second = 10.0

        gmail_service._rate_limit()
        time.sleep(0.15)  # Wait longer than required interval

        start_time = time.time()
        gmail_service._rate_limit()
        elapsed = time.time() - start_time

        # Should be nearly instant
        assert elapsed < 0.05


# ============================================================
# Email Listing Tests
# ============================================================


class TestListMessages:
    """Test listing messages from Gmail API."""

    def test_list_messages_basic(self, gmail_service, mock_gmail_api):
        """Test basic message listing."""
        gmail_service.service = mock_gmail_api

        mock_result = {
            "messages": [
                {"id": "msg_1", "threadId": "thread_1"},
                {"id": "msg_2", "threadId": "thread_2"}
            ]
        }

        mock_gmail_api.users().messages().list().execute.return_value = mock_result

        result = gmail_service.list_messages(query="after:2026/01/01", max_results=10)

        assert len(result["messages"]) == 2
        assert result["messages"][0]["id"] == "msg_1"

    def test_list_messages_with_pagination(self, gmail_service, mock_gmail_api):
        """Test message listing with pagination token."""
        gmail_service.service = mock_gmail_api

        mock_result = {
            "messages": [{"id": "msg_3", "threadId": "thread_3"}],
            "nextPageToken": "next_page_token_456"
        }

        mock_gmail_api.users().messages().list().execute.return_value = mock_result

        result = gmail_service.list_messages(page_token="page_token_123")

        assert "nextPageToken" in result
        assert result["nextPageToken"] == "next_page_token_456"

    def test_list_messages_http_error(self, gmail_service, mock_gmail_api):
        """Test handling HTTP errors during listing."""
        gmail_service.service = mock_gmail_api

        # Simulate HTTP error
        error_response = Mock()
        error_response.status = 500
        error_response.reason = "Internal Server Error"

        mock_gmail_api.users().messages().list().execute.side_effect = HttpError(
            resp=error_response, content=b"Error"
        )

        with pytest.raises(HttpError):
            gmail_service.list_messages()


# ============================================================
# Email Fetching Tests
# ============================================================


class TestGetMessage:
    """Test fetching individual messages."""

    def test_get_message(self, gmail_service, mock_gmail_api, sample_raw_message):
        """Test fetching a single message."""
        gmail_service.service = mock_gmail_api

        mock_gmail_api.users().messages().get().execute.return_value = sample_raw_message

        result = gmail_service.get_message("msg_12345")

        assert result["id"] == "msg_12345"
        assert result["threadId"] == "thread_67890"

    def test_get_message_with_format(self, gmail_service, mock_gmail_api, sample_raw_message):
        """Test fetching message with specific format."""
        gmail_service.service = mock_gmail_api

        mock_gmail_api.users().messages().get().execute.return_value = sample_raw_message

        gmail_service.get_message("msg_12345", format="metadata")

        # Verify format parameter was passed
        call_args = mock_gmail_api.users().messages().get.call_args
        assert call_args[1]["format"] == "metadata"


# ============================================================
# Email Parsing Tests
# ============================================================


class TestParseMessage:
    """Test parsing raw Gmail messages into EmailData."""

    def test_parse_simple_message(self, gmail_service, sample_raw_message):
        """Test parsing a simple text message."""
        email = gmail_service.parse_message(sample_raw_message)

        assert isinstance(email, EmailData)
        assert email.message_id == "msg_12345"
        assert email.thread_id == "thread_67890"
        assert email.subject == "Project Update"
        assert email.from_.email == "alice@example.com"
        assert email.from_.name == "Alice Johnson"
        assert len(email.to) == 1
        assert email.to[0].email == "bob@example.com"
        assert len(email.cc) == 1
        assert email.cc[0].email == "charlie@example.com"
        assert not email.is_read
        assert not email.is_starred
        assert email.account_email == "test@example.com"

    def test_parse_multipart_message(self, gmail_service, sample_multipart_message):
        """Test parsing multipart message with HTML and attachments."""
        email = gmail_service.parse_message(sample_multipart_message)

        assert email.message_id == "msg_99999"
        assert email.body_text  # Should have plain text
        assert email.body_html  # Should have HTML
        assert len(email.attachments) == 1
        assert email.attachments[0].filename == "report.pdf"
        assert email.attachments[0].mime_type == "application/pdf"
        assert email.attachments[0].size_bytes == 51200
        assert email.is_starred
        assert email.is_read  # No UNREAD label

    def test_parse_email_address_with_name(self, gmail_service):
        """Test parsing email address with display name."""
        participant = gmail_service._parse_email_address("John Doe <john@example.com>")

        assert participant.email == "john@example.com"
        assert participant.name == "John Doe"

    def test_parse_email_address_without_name(self, gmail_service):
        """Test parsing email address without display name."""
        participant = gmail_service._parse_email_address("simple@example.com")

        assert participant.email == "simple@example.com"
        assert participant.name is None

    def test_parse_date(self, gmail_service):
        """Test parsing RFC 2822 date strings."""
        date_str = "Mon, 03 Feb 2026 10:30:00 -0800"
        parsed = gmail_service._parse_date(date_str)

        assert isinstance(parsed, datetime)
        assert parsed.year == 2026
        assert parsed.month == 2
        assert parsed.day == 3

    def test_parse_invalid_date(self, gmail_service):
        """Test parsing invalid date returns current datetime."""
        parsed = gmail_service._parse_date("invalid date")

        assert isinstance(parsed, datetime)
        # Should be close to now
        assert (datetime.now() - parsed).total_seconds() < 1


# ============================================================
# Batch Fetching Tests
# ============================================================


class TestFetchEmails:
    """Test batch email fetching."""

    def test_fetch_emails_basic(self, gmail_service, mock_gmail_api, sample_raw_message):
        """Test fetching multiple emails."""
        gmail_service.service = mock_gmail_api

        # Mock list response
        list_result = {
            "messages": [
                {"id": "msg_1", "threadId": "thread_1"},
                {"id": "msg_2", "threadId": "thread_2"}
            ]
        }

        mock_gmail_api.users().messages().list().execute.return_value = list_result
        mock_gmail_api.users().messages().get().execute.return_value = sample_raw_message

        emails = gmail_service.fetch_emails(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 2, 4),
            max_emails=10
        )

        assert len(emails) == 2
        assert all(isinstance(e, EmailData) for e in emails)

    def test_fetch_emails_with_pagination(self, gmail_service, mock_gmail_api, sample_raw_message):
        """Test fetching with pagination."""
        gmail_service.service = mock_gmail_api

        # First page
        page1_result = {
            "messages": [{"id": "msg_1", "threadId": "thread_1"}],
            "nextPageToken": "token_123"
        }

        # Second page
        page2_result = {
            "messages": [{"id": "msg_2", "threadId": "thread_2"}]
        }

        mock_gmail_api.users().messages().list().execute.side_effect = [
            page1_result,
            page2_result
        ]
        mock_gmail_api.users().messages().get().execute.return_value = sample_raw_message

        emails = gmail_service.fetch_emails(max_emails=10)

        assert len(emails) == 2

    def test_fetch_emails_respects_max_limit(self, gmail_service, mock_gmail_api, sample_raw_message):
        """Test that max_emails limit is respected."""
        gmail_service.service = mock_gmail_api

        # Return more messages than limit
        list_result = {
            "messages": [{"id": f"msg_{i}", "threadId": f"thread_{i}"} for i in range(10)]
        }

        mock_gmail_api.users().messages().list().execute.return_value = list_result
        mock_gmail_api.users().messages().get().execute.return_value = sample_raw_message

        emails = gmail_service.fetch_emails(max_emails=5)

        assert len(emails) == 5

    def test_fetch_emails_handles_parse_errors(self, gmail_service, mock_gmail_api):
        """Test that parsing errors don't stop the entire fetch."""
        gmail_service.service = mock_gmail_api

        list_result = {
            "messages": [
                {"id": "msg_1", "threadId": "thread_1"},
                {"id": "msg_2", "threadId": "thread_2"}
            ]
        }

        mock_gmail_api.users().messages().list().execute.return_value = list_result

        # First message succeeds, second fails
        def side_effect_get(*args, **kwargs):
            call_count = mock_gmail_api.users().messages().get().execute.call_count
            if call_count == 1:
                return {"id": "msg_1", "threadId": "thread_1", "payload": {"headers": []}}
            else:
                raise Exception("Parse error")

        mock_gmail_api.users().messages().get().execute.side_effect = side_effect_get

        emails = gmail_service.fetch_emails(max_emails=10)

        # Should get 1 email despite second failing
        assert len(emails) == 1


# ============================================================
# Batch Export Tests
# ============================================================


class TestBatchExport:
    """Test batch export functionality."""

    def test_batch_export_success(self, gmail_service, mock_gmail_api, sample_raw_message, temp_dir):
        """Test successful batch export."""
        gmail_service.service = mock_gmail_api

        list_result = {
            "messages": [{"id": "msg_1", "threadId": "thread_1"}]
        }

        mock_gmail_api.users().messages().list().execute.return_value = list_result
        mock_gmail_api.users().messages().get().execute.return_value = sample_raw_message

        output_dir = temp_dir / "export"

        result = gmail_service.batch_export(
            output_dir=output_dir,
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 2, 4),
            max_emails=10
        )

        assert result.integration_type == IntegrationType.GMAIL
        assert result.items_fetched == 1
        assert result.items_saved == 1
        assert result.items_skipped == 0
        assert len(result.errors) == 0
        assert result.success_rate == 100.0

        # Check files were created
        assert output_dir.exists()
        assert (output_dir / "manifest.json").exists()

    def test_batch_export_creates_date_directories(self, gmail_service, mock_gmail_api,
                                                   sample_raw_message, temp_dir):
        """Test that export creates date-based subdirectories."""
        gmail_service.service = mock_gmail_api

        list_result = {
            "messages": [{"id": "msg_1", "threadId": "thread_1"}]
        }

        mock_gmail_api.users().messages().list().execute.return_value = list_result
        mock_gmail_api.users().messages().get().execute.return_value = sample_raw_message

        output_dir = temp_dir / "export"
        gmail_service.batch_export(output_dir=output_dir, max_emails=10)

        # Should create a date directory (2026-02-03 from sample message)
        date_dirs = list(output_dir.glob("20*"))
        assert len(date_dirs) > 0

    def test_batch_export_manifest_content(self, gmail_service, mock_gmail_api,
                                          sample_raw_message, temp_dir):
        """Test manifest file contains correct information."""
        gmail_service.service = mock_gmail_api

        list_result = {
            "messages": [{"id": "msg_1", "threadId": "thread_1"}]
        }

        mock_gmail_api.users().messages().list().execute.return_value = list_result
        mock_gmail_api.users().messages().get().execute.return_value = sample_raw_message

        output_dir = temp_dir / "export"
        gmail_service.batch_export(output_dir=output_dir, max_emails=10)

        manifest_path = output_dir / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)

        assert manifest["account_email"] == "test@example.com"
        assert manifest["total_emails"] == 1
        assert manifest["emails_saved"] == 1
        assert "export_time" in manifest


# ============================================================
# Edge Cases and Error Handling
# ============================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_parse_message_no_subject(self, gmail_service):
        """Test parsing message without subject."""
        raw_message = {
            "id": "msg_1",
            "threadId": "thread_1",
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender@example.com"}
                ]
            }
        }

        email = gmail_service.parse_message(raw_message)

        assert email.subject == "(No Subject)"

    def test_parse_message_no_recipients(self, gmail_service):
        """Test parsing message without recipients."""
        raw_message = {
            "id": "msg_1",
            "threadId": "thread_1",
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Subject", "value": "Test"}
                ]
            }
        }

        email = gmail_service.parse_message(raw_message)

        assert len(email.to) == 0
        assert len(email.cc) == 0

    def test_extract_body_no_data(self, gmail_service):
        """Test extracting body when no data present."""
        payload = {"mimeType": "text/plain"}

        text, html = gmail_service._extract_body(payload)

        assert text == ""
        assert html == ""

    def test_extract_attachments_no_parts(self, gmail_service):
        """Test extracting attachments when no parts."""
        payload = {"mimeType": "text/plain"}

        attachments = gmail_service._extract_attachments(payload)

        assert len(attachments) == 0

    def test_email_data_to_dict(self, gmail_service, sample_raw_message):
        """Test EmailData serialization to dict."""
        email = gmail_service.parse_message(sample_raw_message)

        data_dict = email.to_dict()

        assert isinstance(data_dict, dict)
        assert data_dict["message_id"] == "msg_12345"
        assert data_dict["subject"] == "Project Update"
        assert "from" in data_dict
        assert "to" in data_dict
        assert isinstance(data_dict["date"], str)  # ISO format


# ============================================================
# Integration Tests (marked for skipping in CI)
# ============================================================


@pytest.mark.integration
class TestGmailIntegration:
    """
    Integration tests requiring actual credentials.

    These tests are skipped by default. Run with:
        pytest -m integration
    """

    def test_real_connection(self):
        """Test real Gmail API connection (requires credentials)."""
        pytest.skip("Requires actual Gmail credentials")

    def test_real_fetch(self):
        """Test fetching real emails (requires credentials)."""
        pytest.skip("Requires actual Gmail credentials")
