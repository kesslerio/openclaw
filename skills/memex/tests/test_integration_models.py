"""
Unit tests for integration data models.

Tests cover:
- EmailData and EmailParticipant models
- CalendarEvent and CalendarAttendee models
- IntegrationConfig model
- SyncStatus model
- BatchSyncResult model
- Serialization and deserialization
- Edge cases and validation
"""

import pytest
from datetime import datetime, timedelta
from memex.integrations.models import (
    EmailData,
    EmailParticipant,
    EmailAttachment,
    CalendarEvent,
    CalendarAttendee,
    IntegrationConfig,
    IntegrationType,
    EmailLabel,
    SyncStatus,
    BatchSyncResult,
)


# ============================================================
# EmailParticipant Tests
# ============================================================


class TestEmailParticipant:
    """Test EmailParticipant model."""

    def test_participant_with_name(self):
        """Test participant with name and email."""
        participant = EmailParticipant(
            email="john@example.com",
            name="John Doe"
        )

        assert participant.email == "john@example.com"
        assert participant.name == "John Doe"
        assert str(participant) == "John Doe <john@example.com>"

    def test_participant_without_name(self):
        """Test participant with email only."""
        participant = EmailParticipant(email="simple@example.com")

        assert participant.email == "simple@example.com"
        assert participant.name is None
        assert str(participant) == "simple@example.com"

    def test_participant_equality(self):
        """Test participant equality comparison."""
        p1 = EmailParticipant(email="test@example.com", name="Test")
        p2 = EmailParticipant(email="test@example.com", name="Test")
        p3 = EmailParticipant(email="other@example.com", name="Test")

        assert p1 == p2
        assert p1 != p3


# ============================================================
# EmailAttachment Tests
# ============================================================


class TestEmailAttachment:
    """Test EmailAttachment model."""

    def test_attachment_basic(self):
        """Test basic attachment."""
        attachment = EmailAttachment(
            filename="report.pdf",
            mime_type="application/pdf",
            size_bytes=51200,
            attachment_id="att_12345"
        )

        assert attachment.filename == "report.pdf"
        assert attachment.mime_type == "application/pdf"
        assert attachment.size_bytes == 51200
        assert attachment.attachment_id == "att_12345"

    def test_attachment_without_id(self):
        """Test attachment without ID."""
        attachment = EmailAttachment(
            filename="image.jpg",
            mime_type="image/jpeg",
            size_bytes=2048
        )

        assert attachment.attachment_id is None


# ============================================================
# EmailData Tests
# ============================================================


class TestEmailData:
    """Test EmailData model."""

    @pytest.fixture
    def sample_email(self):
        """Create a sample email."""
        return EmailData(
            message_id="msg_123",
            thread_id="thread_456",
            subject="Test Email",
            from_=EmailParticipant(email="sender@example.com", name="Sender"),
            to=[EmailParticipant(email="recipient@example.com", name="Recipient")],
            cc=[EmailParticipant(email="cc@example.com")],
            date=datetime(2026, 2, 4, 10, 30),
            body_text="Plain text body",
            body_html="<p>HTML body</p>",
            labels=["INBOX", "UNREAD"],
            is_read=False,
            is_starred=True,
            account_email="test@example.com"
        )

    def test_email_creation(self, sample_email):
        """Test creating email data."""
        assert sample_email.message_id == "msg_123"
        assert sample_email.subject == "Test Email"
        assert sample_email.from_.email == "sender@example.com"
        assert len(sample_email.to) == 1
        assert len(sample_email.cc) == 1
        assert not sample_email.is_read
        assert sample_email.is_starred

    def test_email_to_dict(self, sample_email):
        """Test email serialization to dict."""
        data = sample_email.to_dict()

        assert isinstance(data, dict)
        assert data["message_id"] == "msg_123"
        assert data["subject"] == "Test Email"
        assert data["from"]["email"] == "sender@example.com"
        assert len(data["to"]) == 1
        assert len(data["cc"]) == 1
        assert isinstance(data["date"], str)  # ISO format
        assert data["is_read"] is False
        assert data["is_starred"] is True

    def test_email_with_attachments(self):
        """Test email with attachments."""
        email = EmailData(
            message_id="msg_with_att",
            thread_id="thread_1",
            subject="Email with Attachment",
            from_=EmailParticipant(email="sender@example.com"),
            to=[EmailParticipant(email="recipient@example.com")],
            attachments=[
                EmailAttachment(
                    filename="file1.pdf",
                    mime_type="application/pdf",
                    size_bytes=1024
                ),
                EmailAttachment(
                    filename="file2.jpg",
                    mime_type="image/jpeg",
                    size_bytes=2048
                )
            ]
        )

        assert len(email.attachments) == 2
        assert email.attachments[0].filename == "file1.pdf"

        # Test serialization
        data = email.to_dict()
        assert len(data["attachments"]) == 2

    def test_email_minimal_required_fields(self):
        """Test email with only required fields."""
        email = EmailData(
            message_id="msg_minimal",
            thread_id="thread_minimal",
            subject="Minimal",
            from_=EmailParticipant(email="sender@example.com"),
            to=[]
        )

        assert email.message_id == "msg_minimal"
        assert len(email.to) == 0
        assert len(email.cc) == 0
        assert email.body_text == ""
        assert email.is_read is False


# ============================================================
# CalendarAttendee Tests
# ============================================================


class TestCalendarAttendee:
    """Test CalendarAttendee model."""

    def test_attendee_basic(self):
        """Test basic attendee."""
        attendee = CalendarAttendee(
            email="alice@example.com",
            name="Alice Johnson",
            response_status="accepted",
            is_organizer=False,
            is_optional=False
        )

        assert attendee.email == "alice@example.com"
        assert attendee.name == "Alice Johnson"
        assert attendee.response_status == "accepted"
        assert not attendee.is_organizer
        assert not attendee.is_optional

    def test_attendee_organizer(self):
        """Test organizer attendee."""
        organizer = CalendarAttendee(
            email="organizer@example.com",
            name="Organizer",
            is_organizer=True
        )

        assert organizer.is_organizer

    def test_attendee_optional(self):
        """Test optional attendee."""
        optional = CalendarAttendee(
            email="optional@example.com",
            is_optional=True
        )

        assert optional.is_optional
        assert optional.name is None

    def test_attendee_response_statuses(self):
        """Test different response statuses."""
        statuses = ["needsAction", "accepted", "declined", "tentative"]

        for status in statuses:
            attendee = CalendarAttendee(
                email="test@example.com",
                response_status=status
            )
            assert attendee.response_status == status


# ============================================================
# CalendarEvent Tests
# ============================================================


class TestCalendarEvent:
    """Test CalendarEvent model."""

    @pytest.fixture
    def sample_event(self):
        """Create a sample calendar event."""
        return CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Team Meeting",
            description="Weekly sync",
            location="Conference Room A",
            start=datetime(2026, 2, 4, 10, 0),
            end=datetime(2026, 2, 4, 11, 0),
            all_day=False,
            attendees=[
                CalendarAttendee(
                    email="alice@example.com",
                    name="Alice",
                    response_status="accepted",
                    is_organizer=True
                ),
                CalendarAttendee(
                    email="bob@example.com",
                    name="Bob",
                    response_status="tentative"
                )
            ],
            organizer=CalendarAttendee(
                email="alice@example.com",
                name="Alice",
                is_organizer=True
            ),
            status="confirmed",
            account_email="test@example.com"
        )

    def test_event_creation(self, sample_event):
        """Test creating calendar event."""
        assert sample_event.event_id == "event_123"
        assert sample_event.summary == "Team Meeting"
        assert sample_event.location == "Conference Room A"
        assert not sample_event.all_day
        assert len(sample_event.attendees) == 2
        assert sample_event.organizer.email == "alice@example.com"

    def test_event_to_dict(self, sample_event):
        """Test event serialization to dict."""
        data = sample_event.to_dict()

        assert isinstance(data, dict)
        assert data["event_id"] == "event_123"
        assert data["summary"] == "Team Meeting"
        assert isinstance(data["start"], str)  # ISO format
        assert isinstance(data["end"], str)  # ISO format
        assert len(data["attendees"]) == 2
        assert data["organizer"]["email"] == "alice@example.com"

    def test_all_day_event(self):
        """Test all-day event."""
        event = CalendarEvent(
            event_id="all_day_event",
            calendar_id="primary",
            summary="Holiday",
            start=datetime(2026, 12, 25),
            end=datetime(2026, 12, 26),
            all_day=True
        )

        assert event.all_day

    def test_event_with_recurrence(self):
        """Test recurring event."""
        event = CalendarEvent(
            event_id="recurring_event",
            calendar_id="primary",
            summary="Weekly Standup",
            start=datetime(2026, 2, 4, 9, 0),
            end=datetime(2026, 2, 4, 9, 30),
            recurrence=["RRULE:FREQ=WEEKLY;BYDAY=TU"],
            recurring_event_id="parent_123"
        )

        assert event.recurrence is not None
        assert len(event.recurrence) == 1
        assert event.recurring_event_id == "parent_123"

    def test_event_with_meet_link(self):
        """Test event with Google Meet link."""
        event = CalendarEvent(
            event_id="virtual_event",
            calendar_id="primary",
            summary="Virtual Meeting",
            start=datetime(2026, 2, 4, 14, 0),
            end=datetime(2026, 2, 4, 15, 0),
            hangout_link="https://meet.google.com/abc-defg-hij",
            meet_link="https://meet.google.com/abc-defg-hij"
        )

        assert event.hangout_link is not None
        assert event.meet_link is not None

    def test_event_minimal_required_fields(self):
        """Test event with only required fields."""
        event = CalendarEvent(
            event_id="minimal_event",
            calendar_id="primary",
            summary="Minimal Event"
        )

        assert event.event_id == "minimal_event"
        assert event.description == ""
        assert event.location == ""
        assert len(event.attendees) == 0
        assert event.organizer is None


# ============================================================
# IntegrationConfig Tests
# ============================================================


class TestIntegrationConfig:
    """Test IntegrationConfig model."""

    def test_default_config(self):
        """Test default configuration."""
        config = IntegrationConfig()

        assert config.credentials_path == "credentials.json"
        assert config.token_dir == ".tokens"
        assert config.data_dir == "./data/integrations"
        assert config.gmail_requests_per_second == 5.0
        assert config.calendar_requests_per_second == 5.0
        assert config.gmail_batch_size == 100
        assert config.calendar_batch_size == 2500
        assert config.max_retries == 3

    def test_custom_config(self):
        """Test custom configuration."""
        config = IntegrationConfig(
            credentials_path="/custom/creds.json",
            token_dir="/custom/tokens",
            data_dir="/custom/data",
            gmail_requests_per_second=10.0,
            max_retries=5
        )

        assert config.credentials_path == "/custom/creds.json"
        assert config.token_dir == "/custom/tokens"
        assert config.data_dir == "/custom/data"
        assert config.gmail_requests_per_second == 10.0
        assert config.max_retries == 5

    def test_gmail_scopes(self):
        """Test Gmail scopes."""
        config = IntegrationConfig()

        assert "https://www.googleapis.com/auth/gmail.readonly" in config.gmail_scopes
        assert "https://www.googleapis.com/auth/gmail.modify" in config.gmail_scopes

    def test_calendar_scopes(self):
        """Test Calendar scopes."""
        config = IntegrationConfig()

        assert "https://www.googleapis.com/auth/calendar.readonly" in config.calendar_scopes


# ============================================================
# SyncStatus Tests
# ============================================================


class TestSyncStatus:
    """Test SyncStatus model."""

    def test_sync_status_initial(self):
        """Test initial sync status."""
        status = SyncStatus(
            integration_type=IntegrationType.GMAIL,
            account_email="test@example.com"
        )

        assert status.integration_type == IntegrationType.GMAIL
        assert status.account_email == "test@example.com"
        assert status.last_sync is None
        assert status.total_items_synced == 0
        assert not status.is_syncing

    def test_sync_status_after_sync(self):
        """Test sync status after successful sync."""
        now = datetime.now()
        status = SyncStatus(
            integration_type=IntegrationType.CALENDAR,
            account_email="test@example.com",
            last_sync=now,
            last_sync_token="token_123",
            total_items_synced=150,
            is_syncing=False
        )

        assert status.last_sync == now
        assert status.last_sync_token == "token_123"
        assert status.total_items_synced == 150
        assert not status.is_syncing

    def test_sync_status_with_error(self):
        """Test sync status with error."""
        status = SyncStatus(
            integration_type=IntegrationType.GMAIL,
            account_email="test@example.com",
            last_error="Connection timeout"
        )

        assert status.last_error == "Connection timeout"

    def test_sync_status_to_dict(self):
        """Test sync status serialization."""
        now = datetime.now()
        status = SyncStatus(
            integration_type=IntegrationType.GMAIL,
            account_email="test@example.com",
            last_sync=now,
            total_items_synced=100
        )

        data = status.to_dict()

        assert isinstance(data, dict)
        assert data["integration_type"] == "gmail"
        assert data["account_email"] == "test@example.com"
        assert isinstance(data["last_sync"], str)  # ISO format
        assert data["total_items_synced"] == 100


# ============================================================
# BatchSyncResult Tests
# ============================================================


class TestBatchSyncResult:
    """Test BatchSyncResult model."""

    def test_sync_result_success(self):
        """Test successful sync result."""
        start = datetime.now()
        end = start + timedelta(seconds=30)

        result = BatchSyncResult(
            integration_type=IntegrationType.GMAIL,
            account_email="test@example.com",
            start_time=start,
            end_time=end,
            items_fetched=100,
            items_saved=100,
            items_skipped=0,
            errors=[]
        )

        assert result.items_fetched == 100
        assert result.items_saved == 100
        assert result.items_skipped == 0
        assert len(result.errors) == 0
        assert result.duration_seconds == 30.0
        assert result.success_rate == 100.0

    def test_sync_result_partial_success(self):
        """Test partial success sync result."""
        start = datetime.now()
        end = start + timedelta(seconds=45)

        result = BatchSyncResult(
            integration_type=IntegrationType.CALENDAR,
            account_email="test@example.com",
            start_time=start,
            end_time=end,
            items_fetched=100,
            items_saved=80,
            items_skipped=20,
            errors=["Error 1", "Error 2"]
        )

        assert result.items_fetched == 100
        assert result.items_saved == 80
        assert result.items_skipped == 20
        assert len(result.errors) == 2
        assert result.duration_seconds == 45.0
        assert result.success_rate == 80.0

    def test_sync_result_zero_items(self):
        """Test sync result with zero items."""
        start = datetime.now()
        end = start + timedelta(seconds=5)

        result = BatchSyncResult(
            integration_type=IntegrationType.GMAIL,
            account_email="test@example.com",
            start_time=start,
            end_time=end,
            items_fetched=0,
            items_saved=0,
            items_skipped=0
        )

        assert result.success_rate == 0.0

    def test_sync_result_to_dict(self):
        """Test sync result serialization."""
        start = datetime.now()
        end = start + timedelta(seconds=60)

        result = BatchSyncResult(
            integration_type=IntegrationType.GMAIL,
            account_email="test@example.com",
            start_time=start,
            end_time=end,
            items_fetched=100,
            items_saved=95,
            items_skipped=5,
            errors=["Error 1"]
        )

        data = result.to_dict()

        assert isinstance(data, dict)
        assert data["integration_type"] == "gmail"
        assert data["account_email"] == "test@example.com"
        assert isinstance(data["start_time"], str)  # ISO format
        assert isinstance(data["end_time"], str)  # ISO format
        assert data["duration_seconds"] == 60.0
        assert data["items_fetched"] == 100
        assert data["items_saved"] == 95
        assert data["success_rate"] == 95.0
        assert len(data["errors"]) == 1


# ============================================================
# Enum Tests
# ============================================================


class TestEnums:
    """Test enum values."""

    def test_integration_type_values(self):
        """Test IntegrationType enum values."""
        assert IntegrationType.GMAIL.value == "gmail"
        assert IntegrationType.CALENDAR.value == "calendar"
        assert IntegrationType.PLAUD.value == "plaud"

    def test_email_label_values(self):
        """Test EmailLabel enum values."""
        assert EmailLabel.INBOX.value == "INBOX"
        assert EmailLabel.SENT.value == "SENT"
        assert EmailLabel.UNREAD.value == "UNREAD"
        assert EmailLabel.STARRED.value == "STARRED"


# ============================================================
# Edge Cases
# ============================================================


class TestModelEdgeCases:
    """Test edge cases and validation."""

    def test_email_empty_recipients(self):
        """Test email with no recipients."""
        email = EmailData(
            message_id="msg_1",
            thread_id="thread_1",
            subject="No recipients",
            from_=EmailParticipant(email="sender@example.com"),
            to=[],
            cc=[],
            bcc=[]
        )

        data = email.to_dict()
        assert len(data["to"]) == 0
        assert len(data["cc"]) == 0
        assert len(data["bcc"]) == 0

    def test_calendar_event_no_attendees(self):
        """Test calendar event with no attendees."""
        event = CalendarEvent(
            event_id="event_1",
            calendar_id="primary",
            summary="Solo Event",
            attendees=[]
        )

        data = event.to_dict()
        assert len(data["attendees"]) == 0
        assert data["organizer"] is None

    def test_batch_result_duration_calculation(self):
        """Test duration calculation in batch result."""
        start = datetime(2026, 2, 4, 10, 0, 0)
        end = datetime(2026, 2, 4, 10, 2, 30)

        result = BatchSyncResult(
            integration_type=IntegrationType.GMAIL,
            account_email="test@example.com",
            start_time=start,
            end_time=end,
            items_fetched=10,
            items_saved=10,
            items_skipped=0
        )

        assert result.duration_seconds == 150.0  # 2 minutes 30 seconds

    def test_email_participant_special_characters(self):
        """Test participant with special characters in name."""
        participant = EmailParticipant(
            email="test@example.com",
            name="O'Brien, Sr. (PhD)"
        )

        assert participant.name == "O'Brien, Sr. (PhD)"
        assert str(participant) == "O'Brien, Sr. (PhD) <test@example.com>"
