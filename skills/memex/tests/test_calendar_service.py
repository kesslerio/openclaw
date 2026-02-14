"""
Unit tests for CalendarService.

Tests cover:
- Service initialization and configuration
- OAuth credential management
- Event fetching and parsing
- Calendar listing
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

from memex.integrations.calendar_service import (
    CalendarService,
    CalendarConfig,
    CalendarCredentials,
)
from memex.integrations.models import (
    CalendarEvent,
    CalendarAttendee,
    IntegrationType,
)


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def calendar_config(temp_dir):
    """Calendar configuration for testing."""
    return CalendarConfig(
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
        "scopes": ["https://www.googleapis.com/auth/calendar.readonly"]
    })
    return creds


@pytest.fixture
def calendar_service(calendar_config, mock_credentials):
    """CalendarService instance with mocked credentials."""
    service = CalendarService(config=calendar_config, account_email="test@example.com")

    # Mock the credentials manager
    service.credentials_manager.credentials = mock_credentials
    service.credentials_manager.get_credentials = Mock(return_value=mock_credentials)

    return service


@pytest.fixture
def mock_calendar_api():
    """Mock Calendar API service."""
    api = MagicMock()

    # Mock the events() chain
    events_api = MagicMock()
    api.events.return_value = events_api

    # Mock the calendarList() chain
    calendar_list_api = MagicMock()
    api.calendarList.return_value = calendar_list_api

    return api


@pytest.fixture
def sample_calendar_event():
    """Sample Calendar API event."""
    return {
        "id": "event_12345",
        "summary": "Team Standup",
        "description": "Daily team sync meeting",
        "location": "Conference Room A",
        "status": "confirmed",
        "visibility": "default",
        "start": {
            "dateTime": "2026-02-04T10:00:00-08:00",
            "timeZone": "America/Los_Angeles"
        },
        "end": {
            "dateTime": "2026-02-04T10:30:00-08:00",
            "timeZone": "America/Los_Angeles"
        },
        "attendees": [
            {
                "email": "alice@example.com",
                "displayName": "Alice Johnson",
                "responseStatus": "accepted",
                "organizer": True
            },
            {
                "email": "bob@example.com",
                "displayName": "Bob Smith",
                "responseStatus": "tentative",
                "optional": False
            }
        ],
        "organizer": {
            "email": "alice@example.com",
            "displayName": "Alice Johnson"
        },
        "created": "2026-02-01T12:00:00Z",
        "updated": "2026-02-02T14:30:00Z",
        "hangoutLink": "https://meet.google.com/abc-defg-hij"
    }


@pytest.fixture
def sample_all_day_event():
    """Sample all-day Calendar event."""
    return {
        "id": "event_67890",
        "summary": "Company Holiday",
        "status": "confirmed",
        "start": {
            "date": "2026-12-25"
        },
        "end": {
            "date": "2026-12-26"
        },
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_recurring_event():
    """Sample recurring Calendar event."""
    return {
        "id": "event_recurring_999",
        "summary": "Weekly Team Meeting",
        "description": "Recurring team sync",
        "start": {
            "dateTime": "2026-02-04T14:00:00-08:00"
        },
        "end": {
            "dateTime": "2026-02-04T15:00:00-08:00"
        },
        "recurrence": [
            "RRULE:FREQ=WEEKLY;BYDAY=TU"
        ],
        "recurringEventId": "recurring_parent_123",
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-15T10:00:00Z"
    }


# ============================================================
# CalendarConfig Tests
# ============================================================


class TestCalendarConfig:
    """Test CalendarConfig initialization and defaults."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CalendarConfig()

        assert config.credentials_path == "credentials.json"
        assert config.token_dir == ".tokens"
        assert config.requests_per_second == 5.0
        assert "https://www.googleapis.com/auth/calendar.readonly" in config.scopes

    def test_custom_config(self):
        """Test custom configuration values."""
        config = CalendarConfig(
            credentials_path="/custom/creds.json",
            token_dir="/custom/tokens",
            scopes=["https://www.googleapis.com/auth/calendar.readonly"],
            requests_per_second=10.0
        )

        assert config.credentials_path == "/custom/creds.json"
        assert config.token_dir == "/custom/tokens"
        assert config.requests_per_second == 10.0
        assert len(config.scopes) == 1


# ============================================================
# CalendarCredentials Tests
# ============================================================


class TestCalendarCredentials:
    """Test OAuth credential management."""

    def test_initialization(self, calendar_config):
        """Test credentials manager initialization."""
        creds_manager = CalendarCredentials(calendar_config, "test@example.com")

        assert creds_manager.account_email == "test@example.com"
        assert creds_manager.config == calendar_config
        assert "calendar_test@example.com.json" in str(creds_manager.token_path)

    def test_get_credentials_valid(self, calendar_config, mock_credentials):
        """Test getting valid credentials."""
        creds_manager = CalendarCredentials(calendar_config, "test@example.com")
        creds_manager.credentials = mock_credentials

        result = creds_manager.get_credentials()

        assert result == mock_credentials
        assert result.valid

    def test_get_credentials_missing_raises_error(self, calendar_config):
        """Test that missing credentials raises ValueError."""
        creds_manager = CalendarCredentials(calendar_config, "test@example.com")

        with pytest.raises(ValueError, match="No valid credentials"):
            creds_manager.get_credentials()

    def test_save_credentials(self, calendar_config, mock_credentials, temp_dir):
        """Test saving credentials to file."""
        creds_manager = CalendarCredentials(calendar_config, "test@example.com")
        creds_manager.credentials = mock_credentials

        creds_manager._save_credentials()

        assert creds_manager.token_path.exists()
        assert creds_manager.token_path.parent.exists()


# ============================================================
# CalendarService Initialization Tests
# ============================================================


class TestCalendarServiceInit:
    """Test CalendarService initialization."""

    def test_init_with_config(self, calendar_config):
        """Test initialization with custom config."""
        service = CalendarService(config=calendar_config, account_email="test@example.com")

        assert service.config == calendar_config
        assert service.account_email == "test@example.com"
        assert service.service is None
        assert service._last_request_time == 0.0

    def test_init_default_config(self):
        """Test initialization with default config."""
        service = CalendarService(account_email="test@example.com")

        assert service.config is not None
        assert service.account_email == "test@example.com"


# ============================================================
# Connection and Authentication Tests
# ============================================================


class TestCalendarServiceConnection:
    """Test Calendar API connection."""

    @patch('memex.integrations.calendar_service.build')
    def test_connect(self, mock_build, calendar_service, mock_credentials):
        """Test connecting to Calendar API."""
        mock_api = MagicMock()
        mock_build.return_value = mock_api

        calendar_service.connect()

        mock_build.assert_called_once_with("calendar", "v3", credentials=mock_credentials)
        assert calendar_service.service == mock_api

    @patch('memex.integrations.calendar_service.build')
    def test_authorize(self, mock_build, calendar_service, mock_credentials):
        """Test authorization flow."""
        mock_api = MagicMock()
        mock_build.return_value = mock_api

        # Mock authorize to avoid actual OAuth flow
        calendar_service.credentials_manager.authorize = Mock(return_value=mock_credentials)

        calendar_service.authorize()

        calendar_service.credentials_manager.authorize.assert_called_once()
        assert calendar_service.service == mock_api


# ============================================================
# Rate Limiting Tests
# ============================================================


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_enforced(self, calendar_service):
        """Test that rate limiting delays requests."""
        calendar_service.config.requests_per_second = 10.0  # 100ms between requests

        start_time = time.time()

        # First request - no delay
        calendar_service._rate_limit()

        # Second request - should be delayed
        calendar_service._rate_limit()

        elapsed = time.time() - start_time

        # Should take at least 100ms (0.1 seconds)
        assert elapsed >= 0.09  # Allow small margin

    def test_rate_limit_no_delay_when_enough_time_passed(self, calendar_service):
        """Test no delay when enough time has passed."""
        calendar_service.config.requests_per_second = 10.0

        calendar_service._rate_limit()
        time.sleep(0.15)  # Wait longer than required interval

        start_time = time.time()
        calendar_service._rate_limit()
        elapsed = time.time() - start_time

        # Should be nearly instant
        assert elapsed < 0.05


# ============================================================
# Calendar Listing Tests
# ============================================================


class TestListCalendars:
    """Test listing calendars."""

    def test_list_calendars(self, calendar_service, mock_calendar_api):
        """Test listing all calendars."""
        calendar_service.service = mock_calendar_api

        mock_result = {
            "items": [
                {
                    "id": "primary",
                    "summary": "Test User",
                    "primary": True
                },
                {
                    "id": "work@example.com",
                    "summary": "Work Calendar",
                    "primary": False
                }
            ]
        }

        mock_calendar_api.calendarList().list().execute.return_value = mock_result

        calendars = calendar_service.list_calendars()

        assert len(calendars) == 2
        assert calendars[0]["id"] == "primary"
        assert calendars[1]["id"] == "work@example.com"

    def test_list_calendars_error(self, calendar_service, mock_calendar_api):
        """Test handling errors when listing calendars."""
        calendar_service.service = mock_calendar_api

        error_response = Mock()
        error_response.status = 403
        error_response.reason = "Forbidden"

        mock_calendar_api.calendarList().list().execute.side_effect = HttpError(
            resp=error_response, content=b"Error"
        )

        with pytest.raises(HttpError):
            calendar_service.list_calendars()


# ============================================================
# Event Listing Tests
# ============================================================


class TestListEvents:
    """Test listing calendar events."""

    def test_list_events_basic(self, calendar_service, mock_calendar_api, sample_calendar_event):
        """Test basic event listing."""
        calendar_service.service = mock_calendar_api

        mock_result = {
            "items": [sample_calendar_event]
        }

        mock_calendar_api.events().list().execute.return_value = mock_result

        result = calendar_service.list_events(calendar_id="primary")

        assert len(result["items"]) == 1
        assert result["items"][0]["id"] == "event_12345"

    def test_list_events_with_time_range(self, calendar_service, mock_calendar_api):
        """Test listing events with time range."""
        calendar_service.service = mock_calendar_api

        mock_result = {"items": []}
        mock_calendar_api.events().list().execute.return_value = mock_result

        start_time = datetime(2026, 2, 1)
        end_time = datetime(2026, 2, 28)

        calendar_service.list_events(
            calendar_id="primary",
            time_min=start_time,
            time_max=end_time
        )

        call_args = mock_calendar_api.events().list.call_args
        assert "timeMin" in call_args[1]
        assert "timeMax" in call_args[1]

    def test_list_events_with_pagination(self, calendar_service, mock_calendar_api):
        """Test event listing with pagination."""
        calendar_service.service = mock_calendar_api

        mock_result = {
            "items": [],
            "nextPageToken": "next_token_123"
        }

        mock_calendar_api.events().list().execute.return_value = mock_result

        result = calendar_service.list_events(page_token="current_token")

        assert "nextPageToken" in result
        call_args = mock_calendar_api.events().list.call_args
        assert call_args[1]["pageToken"] == "current_token"


# ============================================================
# Event Parsing Tests
# ============================================================


class TestParseEvent:
    """Test parsing raw Calendar events into CalendarEvent."""

    def test_parse_regular_event(self, calendar_service, sample_calendar_event):
        """Test parsing a regular timed event."""
        event = calendar_service.parse_event(sample_calendar_event, "primary")

        assert isinstance(event, CalendarEvent)
        assert event.event_id == "event_12345"
        assert event.calendar_id == "primary"
        assert event.summary == "Team Standup"
        assert event.description == "Daily team sync meeting"
        assert event.location == "Conference Room A"
        assert not event.all_day
        assert len(event.attendees) == 2
        assert event.attendees[0].email == "alice@example.com"
        assert event.attendees[0].is_organizer
        assert event.attendees[1].response_status == "tentative"
        assert event.organizer.email == "alice@example.com"
        assert event.hangout_link == "https://meet.google.com/abc-defg-hij"
        assert event.account_email == "test@example.com"

    def test_parse_all_day_event(self, calendar_service, sample_all_day_event):
        """Test parsing an all-day event."""
        event = calendar_service.parse_event(sample_all_day_event, "primary")

        assert event.all_day
        assert event.summary == "Company Holiday"
        assert isinstance(event.start, datetime)
        assert isinstance(event.end, datetime)

    def test_parse_recurring_event(self, calendar_service, sample_recurring_event):
        """Test parsing a recurring event."""
        event = calendar_service.parse_event(sample_recurring_event, "primary")

        assert event.summary == "Weekly Team Meeting"
        assert event.recurrence is not None
        assert len(event.recurrence) == 1
        assert "RRULE:FREQ=WEEKLY" in event.recurrence[0]
        assert event.recurring_event_id == "recurring_parent_123"

    def test_parse_event_no_attendees(self, calendar_service):
        """Test parsing event without attendees."""
        raw_event = {
            "id": "event_solo",
            "summary": "Personal Task",
            "start": {"dateTime": "2026-02-04T10:00:00-08:00"},
            "end": {"dateTime": "2026-02-04T11:00:00-08:00"}
        }

        event = calendar_service.parse_event(raw_event, "primary")

        assert len(event.attendees) == 0
        assert event.organizer is None

    def test_parse_event_with_meet_link(self, calendar_service):
        """Test parsing event with Google Meet link."""
        raw_event = {
            "id": "event_meet",
            "summary": "Virtual Meeting",
            "start": {"dateTime": "2026-02-04T10:00:00-08:00"},
            "end": {"dateTime": "2026-02-04T11:00:00-08:00"},
            "conferenceData": {
                "entryPoints": [
                    {
                        "entryPointType": "video",
                        "uri": "https://meet.google.com/xyz-abcd-efg"
                    }
                ]
            }
        }

        event = calendar_service.parse_event(raw_event, "primary")

        assert event.meet_link == "https://meet.google.com/xyz-abcd-efg"

    def test_parse_datetime(self, calendar_service):
        """Test parsing ISO 8601 datetime strings."""
        dt_str = "2026-02-04T10:30:00-08:00"
        parsed = calendar_service._parse_datetime(dt_str)

        assert isinstance(parsed, datetime)
        assert parsed.year == 2026
        assert parsed.month == 2
        assert parsed.day == 4

    def test_parse_datetime_with_z(self, calendar_service):
        """Test parsing datetime with Z timezone."""
        dt_str = "2026-02-04T10:30:00Z"
        parsed = calendar_service._parse_datetime(dt_str)

        assert isinstance(parsed, datetime)

    def test_parse_invalid_datetime(self, calendar_service):
        """Test parsing invalid datetime returns None."""
        parsed = calendar_service._parse_datetime("invalid")

        assert parsed is None


# ============================================================
# Batch Fetching Tests
# ============================================================


class TestFetchEvents:
    """Test batch event fetching."""

    def test_fetch_events_basic(self, calendar_service, mock_calendar_api, sample_calendar_event):
        """Test fetching multiple events."""
        calendar_service.service = mock_calendar_api

        mock_result = {
            "items": [sample_calendar_event, sample_calendar_event]
        }

        mock_calendar_api.events().list().execute.return_value = mock_result

        events = calendar_service.fetch_events(
            calendar_id="primary",
            start_date=datetime(2026, 2, 1),
            end_date=datetime(2026, 2, 28),
            max_events=10
        )

        assert len(events) == 2
        assert all(isinstance(e, CalendarEvent) for e in events)

    def test_fetch_events_with_pagination(self, calendar_service, mock_calendar_api,
                                         sample_calendar_event):
        """Test fetching with pagination."""
        calendar_service.service = mock_calendar_api

        # First page
        page1_result = {
            "items": [sample_calendar_event],
            "nextPageToken": "token_123"
        }

        # Second page
        page2_result = {
            "items": [sample_calendar_event]
        }

        mock_calendar_api.events().list().execute.side_effect = [
            page1_result,
            page2_result
        ]

        events = calendar_service.fetch_events(max_events=10)

        assert len(events) == 2

    def test_fetch_events_respects_max_limit(self, calendar_service, mock_calendar_api,
                                             sample_calendar_event):
        """Test that max_events limit is respected."""
        calendar_service.service = mock_calendar_api

        # Return many events
        mock_result = {
            "items": [sample_calendar_event] * 10
        }

        mock_calendar_api.events().list().execute.return_value = mock_result

        events = calendar_service.fetch_events(max_events=5)

        assert len(events) == 5

    def test_fetch_events_handles_parse_errors(self, calendar_service, mock_calendar_api):
        """Test that parsing errors don't stop the entire fetch."""
        calendar_service.service = mock_calendar_api

        # One valid, one invalid event
        mock_result = {
            "items": [
                {
                    "id": "valid",
                    "summary": "Valid Event",
                    "start": {"dateTime": "2026-02-04T10:00:00Z"},
                    "end": {"dateTime": "2026-02-04T11:00:00Z"}
                },
                {
                    "id": "invalid",
                    # Missing required fields - will cause parse error
                }
            ]
        }

        mock_calendar_api.events().list().execute.return_value = mock_result

        events = calendar_service.fetch_events(max_events=10)

        # Should get 1 event despite second failing
        assert len(events) == 1


# ============================================================
# Batch Export Tests
# ============================================================


class TestBatchExport:
    """Test batch export functionality."""

    def test_batch_export_success(self, calendar_service, mock_calendar_api,
                                  sample_calendar_event, temp_dir):
        """Test successful batch export."""
        calendar_service.service = mock_calendar_api

        mock_result = {
            "items": [sample_calendar_event]
        }

        mock_calendar_api.events().list().execute.return_value = mock_result

        output_dir = temp_dir / "export"

        result = calendar_service.batch_export(
            output_dir=output_dir,
            calendar_id="primary",
            start_date=datetime(2026, 2, 1),
            end_date=datetime(2026, 2, 28),
            max_events=10
        )

        assert result.integration_type == IntegrationType.CALENDAR
        assert result.items_fetched == 1
        assert result.items_saved == 1
        assert result.items_skipped == 0
        assert len(result.errors) == 0
        assert result.success_rate == 100.0

        # Check files were created
        assert output_dir.exists()
        assert (output_dir / "manifest.json").exists()

    def test_batch_export_creates_date_directories(self, calendar_service, mock_calendar_api,
                                                   sample_calendar_event, temp_dir):
        """Test that export creates date-based subdirectories."""
        calendar_service.service = mock_calendar_api

        mock_result = {
            "items": [sample_calendar_event]
        }

        mock_calendar_api.events().list().execute.return_value = mock_result

        output_dir = temp_dir / "export"
        calendar_service.batch_export(output_dir=output_dir, max_events=10)

        # Should create a date directory
        date_dirs = list(output_dir.glob("20*"))
        assert len(date_dirs) > 0

    def test_batch_export_manifest_content(self, calendar_service, mock_calendar_api,
                                          sample_calendar_event, temp_dir):
        """Test manifest file contains correct information."""
        calendar_service.service = mock_calendar_api

        mock_result = {
            "items": [sample_calendar_event]
        }

        mock_calendar_api.events().list().execute.return_value = mock_result

        output_dir = temp_dir / "export"
        calendar_service.batch_export(output_dir=output_dir, max_events=10)

        manifest_path = output_dir / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)

        assert manifest["account_email"] == "test@example.com"
        assert manifest["calendar_id"] == "primary"
        assert manifest["total_events"] == 1
        assert manifest["events_saved"] == 1
        assert "export_time" in manifest


# ============================================================
# Edge Cases and Error Handling
# ============================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_parse_event_no_title(self, calendar_service):
        """Test parsing event without title."""
        raw_event = {
            "id": "event_1",
            "start": {"dateTime": "2026-02-04T10:00:00Z"},
            "end": {"dateTime": "2026-02-04T11:00:00Z"}
        }

        event = calendar_service.parse_event(raw_event, "primary")

        assert event.summary == "(No Title)"

    def test_parse_event_minimal_data(self, calendar_service):
        """Test parsing event with minimal required data."""
        raw_event = {
            "id": "event_minimal",
            "start": {"dateTime": "2026-02-04T10:00:00Z"},
            "end": {"dateTime": "2026-02-04T11:00:00Z"}
        }

        event = calendar_service.parse_event(raw_event, "primary")

        assert event.event_id == "event_minimal"
        assert event.description == ""
        assert event.location == ""
        assert len(event.attendees) == 0

    def test_calendar_event_to_dict(self, calendar_service, sample_calendar_event):
        """Test CalendarEvent serialization to dict."""
        event = calendar_service.parse_event(sample_calendar_event, "primary")

        data_dict = event.to_dict()

        assert isinstance(data_dict, dict)
        assert data_dict["event_id"] == "event_12345"
        assert data_dict["summary"] == "Team Standup"
        assert "attendees" in data_dict
        assert isinstance(data_dict["start"], str)  # ISO format
        assert isinstance(data_dict["end"], str)  # ISO format

    def test_attendee_optional_field(self, calendar_service):
        """Test parsing attendee optional field."""
        raw_event = {
            "id": "event_optional",
            "summary": "Meeting",
            "start": {"dateTime": "2026-02-04T10:00:00Z"},
            "end": {"dateTime": "2026-02-04T11:00:00Z"},
            "attendees": [
                {
                    "email": "required@example.com",
                    "optional": False
                },
                {
                    "email": "optional@example.com",
                    "optional": True
                }
            ]
        }

        event = calendar_service.parse_event(raw_event, "primary")

        assert not event.attendees[0].is_optional
        assert event.attendees[1].is_optional


# ============================================================
# Integration Tests (marked for skipping in CI)
# ============================================================


@pytest.mark.integration
class TestCalendarIntegration:
    """
    Integration tests requiring actual credentials.

    These tests are skipped by default. Run with:
        pytest -m integration
    """

    def test_real_connection(self):
        """Test real Calendar API connection (requires credentials)."""
        pytest.skip("Requires actual Calendar credentials")

    def test_real_fetch(self):
        """Test fetching real events (requires credentials)."""
        pytest.skip("Requires actual Calendar credentials")
