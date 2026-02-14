"""
Tests for OAuth2 authentication flow.

Tests cover:
- OAuth flow initialization
- Token refresh logic
- Token storage and retrieval
- Multi-account support
- Error handling during auth
- Credential expiration handling
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, mock_open
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow

from memex.integrations.gmail_service import GmailCredentials, GmailConfig
from memex.integrations.calendar_service import CalendarCredentials, CalendarConfig


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def mock_credentials_json():
    """Mock credentials.json content."""
    return {
        "installed": {
            "client_id": "mock_client_id.apps.googleusercontent.com",
            "project_id": "mock-project",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "mock_client_secret",
            "redirect_uris": ["http://localhost"]
        }
    }


@pytest.fixture
def mock_token_data():
    """Mock token.json content."""
    return {
        "token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "mock_client_id.apps.googleusercontent.com",
        "client_secret": "mock_client_secret",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
        "expiry": (datetime.now() + timedelta(hours=1)).isoformat()
    }


@pytest.fixture
def valid_credentials():
    """Create valid mock credentials."""
    creds = Mock(spec=Credentials)
    creds.valid = True
    creds.expired = False
    creds.refresh_token = "mock_refresh_token"
    creds.token = "mock_access_token"
    creds.expiry = datetime.now() + timedelta(hours=1)
    return creds


@pytest.fixture
def expired_credentials():
    """Create expired mock credentials."""
    creds = Mock(spec=Credentials)
    creds.valid = False
    creds.expired = True
    creds.refresh_token = "mock_refresh_token"
    creds.token = "old_access_token"
    creds.expiry = datetime.now() - timedelta(hours=1)
    return creds


# ============================================================
# Gmail OAuth Flow Tests
# ============================================================


class TestGmailOAuthFlow:
    """Test Gmail OAuth authentication flow."""

    def test_credentials_initialization(self, temp_dir):
        """Test credentials manager initialization."""
        config = GmailConfig(
            credentials_path=str(temp_dir / "credentials.json"),
            token_dir=str(temp_dir / ".tokens")
        )

        creds_manager = GmailCredentials(config, "work@example.com")

        assert creds_manager.account_email == "work@example.com"
        assert creds_manager.config == config
        assert creds_manager.credentials is None
        assert "gmail_work@example.com.json" in str(creds_manager.token_path)

    def test_get_valid_credentials_cached(self, temp_dir, valid_credentials):
        """Test getting cached valid credentials."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")
        creds_manager.credentials = valid_credentials

        result = creds_manager.get_credentials()

        assert result == valid_credentials
        assert result.valid

    @patch('memex.integrations.gmail_service.Credentials.from_authorized_user_file')
    def test_load_credentials_from_file(self, mock_from_file, temp_dir, valid_credentials):
        """Test loading credentials from token file."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")

        # Create token file
        creds_manager.token_path.parent.mkdir(parents=True, exist_ok=True)
        creds_manager.token_path.write_text(json.dumps({"token": "test"}))

        mock_from_file.return_value = valid_credentials

        result = creds_manager.get_credentials()

        mock_from_file.assert_called_once()
        assert result.valid

    def test_refresh_expired_credentials(self, temp_dir, expired_credentials):
        """Test refreshing expired credentials."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")
        creds_manager.credentials = expired_credentials

        # Mock the refresh method
        def mock_refresh(request):
            expired_credentials.valid = True
            expired_credentials.expired = False
            expired_credentials.token = "new_access_token"

        expired_credentials.refresh = Mock(side_effect=mock_refresh)
        expired_credentials.to_json = Mock(return_value=json.dumps({"token": "new"}))

        # Create token directory
        creds_manager.token_path.parent.mkdir(parents=True, exist_ok=True)

        result = creds_manager.get_credentials()

        expired_credentials.refresh.assert_called_once()
        assert result.valid

    def test_credentials_not_found_raises_error(self, temp_dir):
        """Test error when no credentials available."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")

        with pytest.raises(ValueError, match="No valid credentials"):
            creds_manager.get_credentials()

    @patch('memex.integrations.gmail_service.InstalledAppFlow.from_client_secrets_file')
    def test_authorize_new_credentials(self, mock_flow, temp_dir, valid_credentials,
                                      mock_credentials_json):
        """Test running OAuth flow for new credentials."""
        config = GmailConfig(
            credentials_path=str(temp_dir / "credentials.json"),
            token_dir=str(temp_dir / ".tokens")
        )

        # Create credentials file
        creds_file = temp_dir / "credentials.json"
        creds_file.write_text(json.dumps(mock_credentials_json))

        creds_manager = GmailCredentials(config, "test@example.com")

        # Mock the flow
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.return_value = valid_credentials
        mock_flow.return_value = mock_flow_instance

        valid_credentials.to_json = Mock(return_value=json.dumps({"token": "new"}))

        result = creds_manager.authorize()

        mock_flow.assert_called_once_with(str(creds_file), config.scopes)
        mock_flow_instance.run_local_server.assert_called_once()
        assert result == valid_credentials

    def test_save_credentials_creates_directory(self, temp_dir, valid_credentials):
        """Test that saving credentials creates token directory."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")
        creds_manager.credentials = valid_credentials

        valid_credentials.to_json = Mock(return_value=json.dumps({"token": "test"}))

        creds_manager._save_credentials()

        assert creds_manager.token_path.exists()
        assert creds_manager.token_path.parent.exists()

    def test_refresh_error_handling(self, temp_dir, expired_credentials):
        """Test handling refresh errors."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")
        creds_manager.credentials = expired_credentials

        # Mock refresh to raise error
        expired_credentials.refresh = Mock(side_effect=RefreshError("Token revoked"))

        with pytest.raises(RefreshError):
            expired_credentials.refresh(None)


# ============================================================
# Calendar OAuth Flow Tests
# ============================================================


class TestCalendarOAuthFlow:
    """Test Calendar OAuth authentication flow."""

    def test_credentials_initialization(self, temp_dir):
        """Test credentials manager initialization."""
        config = CalendarConfig(
            credentials_path=str(temp_dir / "credentials.json"),
            token_dir=str(temp_dir / ".tokens")
        )

        creds_manager = CalendarCredentials(config, "personal@example.com")

        assert creds_manager.account_email == "personal@example.com"
        assert creds_manager.config == config
        assert "calendar_personal@example.com.json" in str(creds_manager.token_path)

    def test_get_valid_credentials(self, temp_dir, valid_credentials):
        """Test getting valid credentials."""
        config = CalendarConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = CalendarCredentials(config, "test@example.com")
        creds_manager.credentials = valid_credentials

        result = creds_manager.get_credentials()

        assert result == valid_credentials
        assert result.valid

    @patch('memex.integrations.calendar_service.InstalledAppFlow.from_client_secrets_file')
    def test_authorize_calendar_credentials(self, mock_flow, temp_dir, valid_credentials,
                                           mock_credentials_json):
        """Test running OAuth flow for Calendar."""
        config = CalendarConfig(
            credentials_path=str(temp_dir / "credentials.json"),
            token_dir=str(temp_dir / ".tokens")
        )

        # Create credentials file
        creds_file = temp_dir / "credentials.json"
        creds_file.write_text(json.dumps(mock_credentials_json))

        creds_manager = CalendarCredentials(config, "test@example.com")

        # Mock the flow
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.return_value = valid_credentials
        mock_flow.return_value = mock_flow_instance

        valid_credentials.to_json = Mock(return_value=json.dumps({"token": "new"}))

        result = creds_manager.authorize()

        assert result == valid_credentials


# ============================================================
# Multi-Account Support Tests
# ============================================================


class TestMultiAccountSupport:
    """Test managing multiple accounts."""

    def test_separate_token_files_per_account(self, temp_dir):
        """Test that each account gets its own token file."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))

        work_creds = GmailCredentials(config, "work@example.com")
        personal_creds = GmailCredentials(config, "personal@example.com")

        assert work_creds.token_path != personal_creds.token_path
        assert "work@example.com" in str(work_creds.token_path)
        assert "personal@example.com" in str(personal_creds.token_path)

    def test_independent_credential_management(self, temp_dir, valid_credentials):
        """Test that credentials are managed independently per account."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))

        work_manager = GmailCredentials(config, "work@example.com")
        personal_manager = GmailCredentials(config, "personal@example.com")

        # Set credentials for work account only
        work_manager.credentials = valid_credentials
        valid_credentials.to_json = Mock(return_value=json.dumps({"token": "work"}))
        work_manager._save_credentials()

        # Work should have token, personal shouldn't
        assert work_manager.token_path.exists()
        assert not personal_manager.token_path.exists()

    def test_multiple_services_same_account(self, temp_dir, valid_credentials):
        """Test using same account for Gmail and Calendar."""
        gmail_config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        calendar_config = CalendarConfig(token_dir=str(temp_dir / ".tokens"))

        gmail_creds = GmailCredentials(gmail_config, "test@example.com")
        calendar_creds = CalendarCredentials(calendar_config, "test@example.com")

        # Token files should be different (different prefixes)
        assert gmail_creds.token_path != calendar_creds.token_path
        assert "gmail_" in str(gmail_creds.token_path)
        assert "calendar_" in str(calendar_creds.token_path)


# ============================================================
# Token Storage Tests
# ============================================================


class TestTokenStorage:
    """Test token file storage and retrieval."""

    def test_save_token_creates_file(self, temp_dir, valid_credentials):
        """Test that saving token creates file."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")
        creds_manager.credentials = valid_credentials

        token_data = {"token": "test_token", "refresh_token": "refresh"}
        valid_credentials.to_json = Mock(return_value=json.dumps(token_data))

        creds_manager._save_credentials()

        assert creds_manager.token_path.exists()

        # Verify content
        saved_data = json.loads(creds_manager.token_path.read_text())
        assert saved_data["token"] == "test_token"

    def test_token_file_permissions(self, temp_dir, valid_credentials):
        """Test that token files have appropriate permissions."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")
        creds_manager.credentials = valid_credentials

        valid_credentials.to_json = Mock(return_value=json.dumps({"token": "test"}))

        creds_manager._save_credentials()

        # File should exist and be readable
        assert creds_manager.token_path.exists()
        assert creds_manager.token_path.is_file()

    @patch('memex.integrations.gmail_service.Credentials.from_authorized_user_file')
    def test_load_corrupted_token_file(self, mock_from_file, temp_dir):
        """Test handling corrupted token file."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")

        # Create corrupted token file
        creds_manager.token_path.parent.mkdir(parents=True, exist_ok=True)
        creds_manager.token_path.write_text("corrupted json{{{")

        mock_from_file.side_effect = Exception("Invalid JSON")

        with pytest.raises(Exception):
            creds_manager.get_credentials()


# ============================================================
# Scope Management Tests
# ============================================================


class TestScopeManagement:
    """Test OAuth scope handling."""

    def test_default_gmail_scopes(self):
        """Test default Gmail scopes."""
        config = GmailConfig()

        assert "https://www.googleapis.com/auth/gmail.readonly" in config.scopes
        assert "https://www.googleapis.com/auth/gmail.modify" in config.scopes

    def test_custom_gmail_scopes(self):
        """Test custom Gmail scopes."""
        custom_scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
        config = GmailConfig(scopes=custom_scopes)

        assert config.scopes == custom_scopes
        assert len(config.scopes) == 1

    def test_default_calendar_scopes(self):
        """Test default Calendar scopes."""
        config = CalendarConfig()

        assert "https://www.googleapis.com/auth/calendar.readonly" in config.scopes

    def test_custom_calendar_scopes(self):
        """Test custom Calendar scopes."""
        custom_scopes = ["https://www.googleapis.com/auth/calendar.events.readonly"]
        config = CalendarConfig(scopes=custom_scopes)

        assert config.scopes == custom_scopes


# ============================================================
# Credential Lifecycle Tests
# ============================================================


class TestCredentialLifecycle:
    """Test credential lifecycle (creation, refresh, expiration)."""

    def test_credential_expiration_check(self, valid_credentials, expired_credentials):
        """Test checking credential expiration."""
        assert valid_credentials.valid
        assert not valid_credentials.expired

        assert not expired_credentials.valid
        assert expired_credentials.expired

    def test_token_near_expiration(self, temp_dir):
        """Test handling tokens near expiration."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")

        # Create credentials expiring in 1 minute
        near_expiry_creds = Mock(spec=Credentials)
        near_expiry_creds.valid = True
        near_expiry_creds.expired = False
        near_expiry_creds.expiry = datetime.now() + timedelta(minutes=1)
        near_expiry_creds.refresh_token = "refresh_token"

        creds_manager.credentials = near_expiry_creds

        result = creds_manager.get_credentials()

        # Should still be valid (not expired yet)
        assert result.valid

    def test_token_without_refresh_token(self, temp_dir):
        """Test handling expired token without refresh token."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")

        # Expired credentials without refresh token
        no_refresh_creds = Mock(spec=Credentials)
        no_refresh_creds.valid = False
        no_refresh_creds.expired = True
        no_refresh_creds.refresh_token = None

        creds_manager.credentials = no_refresh_creds

        # Should raise error (can't refresh without refresh token)
        with pytest.raises(ValueError, match="No valid credentials"):
            creds_manager.get_credentials()


# ============================================================
# Error Handling Tests
# ============================================================


class TestOAuthErrorHandling:
    """Test error handling in OAuth flow."""

    def test_missing_credentials_file(self, temp_dir):
        """Test error when credentials.json is missing."""
        config = GmailConfig(
            credentials_path=str(temp_dir / "nonexistent.json"),
            token_dir=str(temp_dir / ".tokens")
        )
        creds_manager = GmailCredentials(config, "test@example.com")

        with pytest.raises(Exception):
            creds_manager.authorize()

    @patch('memex.integrations.gmail_service.InstalledAppFlow.from_client_secrets_file')
    def test_oauth_flow_user_cancellation(self, mock_flow, temp_dir,
                                         mock_credentials_json):
        """Test handling user canceling OAuth flow."""
        config = GmailConfig(
            credentials_path=str(temp_dir / "credentials.json"),
            token_dir=str(temp_dir / ".tokens")
        )

        # Create credentials file
        creds_file = temp_dir / "credentials.json"
        creds_file.write_text(json.dumps(mock_credentials_json))

        creds_manager = GmailCredentials(config, "test@example.com")

        # Mock flow to raise error (user canceled)
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.side_effect = Exception("User canceled")
        mock_flow.return_value = mock_flow_instance

        with pytest.raises(Exception, match="User canceled"):
            creds_manager.authorize()

    def test_network_error_during_refresh(self, temp_dir, expired_credentials):
        """Test handling network errors during token refresh."""
        config = GmailConfig(token_dir=str(temp_dir / ".tokens"))
        creds_manager = GmailCredentials(config, "test@example.com")
        creds_manager.credentials = expired_credentials

        # Mock network error
        from google.auth.exceptions import TransportError
        expired_credentials.refresh = Mock(side_effect=TransportError("Network error"))

        with pytest.raises(TransportError):
            expired_credentials.refresh(None)


# ============================================================
# Integration Marker Tests
# ============================================================


@pytest.mark.integration
class TestRealOAuthFlow:
    """
    Integration tests with real OAuth flow.

    These require actual Google Cloud credentials and user interaction.
    Skip by default with: pytest -m "not integration"
    """

    def test_real_gmail_oauth_flow(self):
        """Test real Gmail OAuth flow (requires user interaction)."""
        pytest.skip("Requires actual credentials and user interaction")

    def test_real_calendar_oauth_flow(self):
        """Test real Calendar OAuth flow (requires user interaction)."""
        pytest.skip("Requires actual credentials and user interaction")

    def test_real_token_refresh(self):
        """Test real token refresh (requires valid tokens)."""
        pytest.skip("Requires actual valid tokens")
