"""
Shared fixtures for integration tests (Gmail and Calendar).

This module provides reusable fixtures for:
- Mock API responses
- Sample data (emails, events, attachments)
- Mock credentials and OAuth flows
- API service mocks
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from google.oauth2.credentials import Credentials

from memex.integrations.models import (
    EmailData,
    EmailParticipant,
    EmailAttachment,
    CalendarEvent,
    CalendarAttendee,
)


# ============================================================
# Credentials and Auth Fixtures
# ============================================================


@pytest.fixture
def mock_google_credentials():
    """Mock Google OAuth2 credentials."""
    creds = Mock(spec=Credentials)
    creds.valid = True
    creds.expired = False
    creds.refresh_token = "mock_refresh_token"
    creds.token = "mock_access_token"
    creds.expiry = datetime.now() + timedelta(hours=1)
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
def expired_google_credentials():
    """Mock expired Google OAuth2 credentials."""
    creds = Mock(spec=Credentials)
    creds.valid = False
    creds.expired = True
    creds.refresh_token = "mock_refresh_token"
    creds.token = "old_token"
    creds.expiry = datetime.now() - timedelta(hours=1)
    return creds


@pytest.fixture
def mock_credentials_json_content():
    """Content for credentials.json file."""
    return {
        "installed": {
            "client_id": "123456789.apps.googleusercontent.com",
            "project_id": "test-project",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "test_client_secret",
            "redirect_uris": ["http://localhost"]
        }
    }


# ============================================================
# Gmail API Mock Fixtures
# ============================================================


@pytest.fixture
def mock_gmail_service():
    """Mock Gmail API service."""
    service = MagicMock()

    # Mock users().messages() chain
    messages = MagicMock()
    service.users.return_value.messages.return_value = messages

    return service


@pytest.fixture
def sample_gmail_list_response():
    """Sample response from Gmail messages.list()."""
    return {
        "messages": [
            {"id": "msg_001", "threadId": "thread_001"},
            {"id": "msg_002", "threadId": "thread_002"},
            {"id": "msg_003", "threadId": "thread_003"}
        ],
        "resultSizeEstimate": 3,
        "nextPageToken": "next_page_token_123"
    }


@pytest.fixture
def sample_gmail_message_full():
    """Sample full Gmail message (text only)."""
    return {
        "id": "18d5e1f2c3a8b5f0",
        "threadId": "18d5e1f2c3a8b5f0",
        "labelIds": ["INBOX", "IMPORTANT", "CATEGORY_PERSONAL"],
        "snippet": "Hey, just wanted to follow up on our meeting...",
        "payload": {
            "mimeType": "text/plain",
            "headers": [
                {"name": "From", "value": "John Doe <john.doe@company.com>"},
                {"name": "To", "value": "jane.smith@company.com"},
                {"name": "Cc", "value": "team@company.com"},
                {"name": "Subject", "value": "Follow-up: Q1 Planning"},
                {"name": "Date", "value": "Mon, 3 Feb 2026 14:30:00 -0800"},
                {"name": "Message-ID", "value": "<CABc123@mail.gmail.com>"},
            ],
            "body": {
                "size": 234,
                "data": "SGV5LCBqdXN0IHdhbnRlZCB0byBmb2xsb3cgdXAgb24gb3VyIG1lZXRpbmcgbGFzdCB3ZWVrLiBQbGVhc2UgcmV2aWV3IHRoZSBhdHRhY2hlZCBkb2N1bWVudC4="
            }
        },
        "sizeEstimate": 2048,
        "internalDate": "1738622400000"
    }


@pytest.fixture
def sample_gmail_message_multipart():
    """Sample multipart Gmail message with attachments."""
    return {
        "id": "18d5e1f2c3a8b5f1",
        "threadId": "18d5e1f2c3a8b5f1",
        "labelIds": ["INBOX", "STARRED"],
        "snippet": "Please review the attached quarterly report...",
        "payload": {
            "mimeType": "multipart/mixed",
            "headers": [
                {"name": "From", "value": "Finance Team <finance@company.com>"},
                {"name": "To", "value": "executives@company.com"},
                {"name": "Subject", "value": "Q1 2026 Financial Report"},
                {"name": "Date", "value": "Tue, 4 Feb 2026 09:00:00 -0800"},
            ],
            "parts": [
                {
                    "partId": "0",
                    "mimeType": "text/plain",
                    "body": {
                        "size": 156,
                        "data": "UGxlYXNlIHJldmlldyB0aGUgYXR0YWNoZWQgcXVhcnRlcmx5IHJlcG9ydC4="
                    }
                },
                {
                    "partId": "1",
                    "mimeType": "text/html",
                    "body": {
                        "size": 312,
                        "data": "PHA+UGxlYXNlIHJldmlldyB0aGUgYXR0YWNoZWQgPGI+cXVhcnRlcmx5IHJlcG9ydDwvYj4uPC9wPg=="
                    }
                },
                {
                    "partId": "2",
                    "mimeType": "application/pdf",
                    "filename": "Q1_2026_Report.pdf",
                    "body": {
                        "attachmentId": "ANGjdJ8wK3y6P2qR5sT7uV9w",
                        "size": 524288
                    }
                },
                {
                    "partId": "3",
                    "mimeType": "application/vnd.ms-excel",
                    "filename": "Financial_Data.xlsx",
                    "body": {
                        "attachmentId": "ANGjdJ8wK3y6P2qR5sT7uV9x",
                        "size": 102400
                    }
                }
            ]
        },
        "sizeEstimate": 650000
    }


# ============================================================
# Calendar API Mock Fixtures
# ============================================================


@pytest.fixture
def mock_calendar_service():
    """Mock Calendar API service."""
    service = MagicMock()

    # Mock events() chain
    events = MagicMock()
    service.events.return_value = events

    # Mock calendarList() chain
    calendar_list = MagicMock()
    service.calendarList.return_value = calendar_list

    return service


@pytest.fixture
def sample_calendar_list_response():
    """Sample response from calendarList.list()."""
    return {
        "kind": "calendar#calendarList",
        "items": [
            {
                "kind": "calendar#calendarListEntry",
                "id": "primary",
                "summary": "Test User",
                "timeZone": "America/Los_Angeles",
                "colorId": "1",
                "backgroundColor": "#9fe1e7",
                "foregroundColor": "#000000",
                "selected": True,
                "accessRole": "owner",
                "primary": True
            },
            {
                "kind": "calendar#calendarListEntry",
                "id": "work_calendar@company.com",
                "summary": "Work Calendar",
                "timeZone": "America/Los_Angeles",
                "colorId": "2",
                "backgroundColor": "#f691b2",
                "foregroundColor": "#000000",
                "selected": True,
                "accessRole": "writer"
            }
        ]
    }


@pytest.fixture
def sample_calendar_events_response():
    """Sample response from events.list()."""
    return {
        "kind": "calendar#events",
        "summary": "Test User",
        "items": [
            {
                "kind": "calendar#event",
                "id": "event_001_meeting",
                "status": "confirmed",
                "htmlLink": "https://www.google.com/calendar/event?eid=...",
                "created": "2026-02-01T10:00:00.000Z",
                "updated": "2026-02-01T10:00:00.000Z",
                "summary": "Team Standup",
                "description": "Daily team sync meeting",
                "location": "Conference Room A",
                "creator": {
                    "email": "alice@company.com",
                    "displayName": "Alice Johnson",
                    "self": True
                },
                "organizer": {
                    "email": "alice@company.com",
                    "displayName": "Alice Johnson",
                    "self": True
                },
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
                        "email": "alice@company.com",
                        "displayName": "Alice Johnson",
                        "organizer": True,
                        "self": True,
                        "responseStatus": "accepted"
                    },
                    {
                        "email": "bob@company.com",
                        "displayName": "Bob Smith",
                        "responseStatus": "accepted"
                    },
                    {
                        "email": "charlie@company.com",
                        "displayName": "Charlie Brown",
                        "optional": True,
                        "responseStatus": "tentative"
                    }
                ],
                "hangoutLink": "https://meet.google.com/abc-defg-hij",
                "conferenceData": {
                    "entryPoints": [
                        {
                            "entryPointType": "video",
                            "uri": "https://meet.google.com/abc-defg-hij",
                            "label": "meet.google.com/abc-defg-hij"
                        }
                    ],
                    "conferenceSolution": {
                        "name": "Google Meet"
                    }
                }
            },
            {
                "kind": "calendar#event",
                "id": "event_002_birthday",
                "status": "confirmed",
                "created": "2026-01-15T08:00:00.000Z",
                "updated": "2026-01-15T08:00:00.000Z",
                "summary": "Sarah's Birthday",
                "start": {
                    "date": "2026-02-15"
                },
                "end": {
                    "date": "2026-02-16"
                },
                "transparency": "transparent"
            },
            {
                "kind": "calendar#event",
                "id": "event_003_recurring",
                "status": "confirmed",
                "created": "2026-01-01T00:00:00.000Z",
                "updated": "2026-02-01T12:00:00.000Z",
                "summary": "Weekly Team Meeting",
                "description": "Recurring team sync every Tuesday",
                "start": {
                    "dateTime": "2026-02-04T14:00:00-08:00",
                    "timeZone": "America/Los_Angeles"
                },
                "end": {
                    "dateTime": "2026-02-04T15:00:00-08:00",
                    "timeZone": "America/Los_Angeles"
                },
                "recurrence": [
                    "RRULE:FREQ=WEEKLY;BYDAY=TU"
                ],
                "recurringEventId": "recurring_parent_weekly_meeting",
                "originalStartTime": {
                    "dateTime": "2026-02-04T14:00:00-08:00",
                    "timeZone": "America/Los_Angeles"
                }
            }
        ],
        "nextPageToken": "next_events_token"
    }


# ============================================================
# Model Instance Fixtures
# ============================================================


@pytest.fixture
def sample_email_data():
    """Sample EmailData instance."""
    return EmailData(
        message_id="msg_sample_123",
        thread_id="thread_sample_456",
        subject="Sample Email for Testing",
        from_=EmailParticipant(
            email="sender@example.com",
            name="Sender Name"
        ),
        to=[
            EmailParticipant(email="recipient1@example.com", name="Recipient One"),
            EmailParticipant(email="recipient2@example.com")
        ],
        cc=[EmailParticipant(email="cc@example.com")],
        date=datetime(2026, 2, 4, 10, 30),
        body_text="This is the plain text body of the email.",
        body_html="<p>This is the <b>HTML</b> body of the email.</p>",
        labels=["INBOX", "IMPORTANT"],
        attachments=[
            EmailAttachment(
                filename="document.pdf",
                mime_type="application/pdf",
                size_bytes=51200,
                attachment_id="att_123"
            )
        ],
        is_read=False,
        is_starred=True,
        account_email="test@example.com"
    )


@pytest.fixture
def sample_calendar_event_data():
    """Sample CalendarEvent instance."""
    return CalendarEvent(
        event_id="event_sample_789",
        calendar_id="primary",
        summary="Sample Meeting",
        description="This is a test meeting",
        location="Zoom",
        start=datetime(2026, 2, 4, 14, 0),
        end=datetime(2026, 2, 4, 15, 0),
        all_day=False,
        attendees=[
            CalendarAttendee(
                email="organizer@example.com",
                name="Organizer Name",
                response_status="accepted",
                is_organizer=True
            ),
            CalendarAttendee(
                email="attendee@example.com",
                name="Attendee Name",
                response_status="tentative",
                is_optional=False
            )
        ],
        organizer=CalendarAttendee(
            email="organizer@example.com",
            name="Organizer Name",
            is_organizer=True
        ),
        status="confirmed",
        meet_link="https://zoom.us/j/123456789",
        created=datetime(2026, 2, 1, 10, 0),
        updated=datetime(2026, 2, 3, 14, 30),
        account_email="test@example.com"
    )


# ============================================================
# Factory Fixtures
# ============================================================


@pytest.fixture
def email_factory():
    """Factory for creating test emails."""
    def _create_email(
        message_id=None,
        subject="Test Email",
        from_email="sender@example.com",
        to_emails=None,
        is_read=False,
        is_starred=False,
        labels=None,
        **kwargs
    ):
        if message_id is None:
            message_id = f"msg_{datetime.now().timestamp()}"

        if to_emails is None:
            to_emails = ["recipient@example.com"]

        if labels is None:
            labels = ["INBOX"]

        return EmailData(
            message_id=message_id,
            thread_id=kwargs.get("thread_id", f"thread_{message_id}"),
            subject=subject,
            from_=EmailParticipant(email=from_email),
            to=[EmailParticipant(email=e) for e in to_emails],
            date=kwargs.get("date", datetime.now()),
            labels=labels,
            is_read=is_read,
            is_starred=is_starred,
            account_email=kwargs.get("account_email", "test@example.com"),
            **{k: v for k, v in kwargs.items() if k not in ["thread_id", "date", "account_email"]}
        )

    return _create_email


@pytest.fixture
def calendar_event_factory():
    """Factory for creating test calendar events."""
    def _create_event(
        event_id=None,
        summary="Test Event",
        start=None,
        end=None,
        all_day=False,
        **kwargs
    ):
        if event_id is None:
            event_id = f"event_{datetime.now().timestamp()}"

        if start is None:
            start = datetime.now() + timedelta(days=1)

        if end is None:
            end = start + timedelta(hours=1)

        return CalendarEvent(
            event_id=event_id,
            calendar_id=kwargs.get("calendar_id", "primary"),
            summary=summary,
            start=start,
            end=end,
            all_day=all_day,
            account_email=kwargs.get("account_email", "test@example.com"),
            **{k: v for k, v in kwargs.items() if k not in ["calendar_id", "account_email"]}
        )

    return _create_event


# ============================================================
# Batch Data Fixtures
# ============================================================


@pytest.fixture
def batch_emails(email_factory):
    """Create a batch of test emails."""
    emails = []
    for i in range(10):
        email = email_factory(
            message_id=f"msg_batch_{i}",
            subject=f"Email #{i}",
            date=datetime.now() - timedelta(days=i),
            is_read=(i % 2 == 0),
            is_starred=(i % 3 == 0)
        )
        emails.append(email)
    return emails


@pytest.fixture
def batch_events(calendar_event_factory):
    """Create a batch of test calendar events."""
    events = []
    for i in range(10):
        start_time = datetime.now() + timedelta(days=i)
        event = calendar_event_factory(
            event_id=f"event_batch_{i}",
            summary=f"Event #{i}",
            start=start_time,
            end=start_time + timedelta(hours=1)
        )
        events.append(event)
    return events
