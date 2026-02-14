"""
Data models for Gmail and Calendar integrations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class IntegrationType(str, Enum):
    """Type of integration"""
    GMAIL = "gmail"
    CALENDAR = "calendar"
    PLAUD = "plaud"


class EmailLabel(str, Enum):
    """Common Gmail labels"""
    INBOX = "INBOX"
    SENT = "SENT"
    DRAFT = "DRAFT"
    SPAM = "SPAM"
    TRASH = "TRASH"
    STARRED = "STARRED"
    IMPORTANT = "IMPORTANT"
    UNREAD = "UNREAD"


@dataclass
class EmailParticipant:
    """Email sender or recipient"""
    email: str
    name: Optional[str] = None

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} <{self.email}>"
        return self.email


@dataclass
class EmailAttachment:
    """Email attachment metadata"""
    filename: str
    mime_type: str
    size_bytes: int
    attachment_id: Optional[str] = None


@dataclass
class EmailData:
    """Structured email data"""
    message_id: str
    thread_id: str
    subject: str
    from_: EmailParticipant
    to: List[EmailParticipant]
    cc: List[EmailParticipant] = field(default_factory=list)
    bcc: List[EmailParticipant] = field(default_factory=list)
    date: datetime = field(default_factory=datetime.now)
    body_text: str = ""
    body_html: str = ""
    labels: List[str] = field(default_factory=list)
    attachments: List[EmailAttachment] = field(default_factory=list)
    is_read: bool = False
    is_starred: bool = False
    account_email: str = ""  # Which account this belongs to
    raw_headers: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "message_id": self.message_id,
            "thread_id": self.thread_id,
            "subject": self.subject,
            "from": {"email": self.from_.email, "name": self.from_.name},
            "to": [{"email": p.email, "name": p.name} for p in self.to],
            "cc": [{"email": p.email, "name": p.name} for p in self.cc],
            "bcc": [{"email": p.email, "name": p.name} for p in self.bcc],
            "date": self.date.isoformat(),
            "body_text": self.body_text,
            "body_html": self.body_html,
            "labels": self.labels,
            "attachments": [
                {
                    "filename": att.filename,
                    "mime_type": att.mime_type,
                    "size_bytes": att.size_bytes,
                    "attachment_id": att.attachment_id
                }
                for att in self.attachments
            ],
            "is_read": self.is_read,
            "is_starred": self.is_starred,
            "account_email": self.account_email,
            "raw_headers": self.raw_headers,
        }


@dataclass
class CalendarAttendee:
    """Calendar event attendee"""
    email: str
    name: Optional[str] = None
    response_status: Optional[str] = None  # needsAction, accepted, declined, tentative
    is_organizer: bool = False
    is_optional: bool = False


@dataclass
class CalendarEvent:
    """Structured calendar event data"""
    event_id: str
    calendar_id: str
    summary: str
    description: str = ""
    location: str = ""
    start: datetime = field(default_factory=datetime.now)
    end: datetime = field(default_factory=datetime.now)
    all_day: bool = False
    attendees: List[CalendarAttendee] = field(default_factory=list)
    organizer: Optional[CalendarAttendee] = None
    status: str = "confirmed"  # confirmed, tentative, cancelled
    visibility: str = "default"  # default, public, private, confidential
    recurrence: Optional[List[str]] = None  # RRULE strings
    recurring_event_id: Optional[str] = None
    hangout_link: Optional[str] = None
    meet_link: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    account_email: str = ""  # Which account this belongs to
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "event_id": self.event_id,
            "calendar_id": self.calendar_id,
            "summary": self.summary,
            "description": self.description,
            "location": self.location,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "all_day": self.all_day,
            "attendees": [
                {
                    "email": att.email,
                    "name": att.name,
                    "response_status": att.response_status,
                    "is_organizer": att.is_organizer,
                    "is_optional": att.is_optional,
                }
                for att in self.attendees
            ],
            "organizer": {
                "email": self.organizer.email,
                "name": self.organizer.name,
            } if self.organizer else None,
            "status": self.status,
            "visibility": self.visibility,
            "recurrence": self.recurrence,
            "recurring_event_id": self.recurring_event_id,
            "hangout_link": self.hangout_link,
            "meet_link": self.meet_link,
            "created": self.created.isoformat() if self.created else None,
            "updated": self.updated.isoformat() if self.updated else None,
            "account_email": self.account_email,
            "raw_data": self.raw_data,
        }


@dataclass
class IntegrationConfig:
    """Configuration for data integrations"""
    # OAuth2 credentials path
    credentials_path: str = "credentials.json"

    # Token storage
    token_dir: str = ".tokens"

    # API scopes
    gmail_scopes: List[str] = field(default_factory=lambda: [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",  # For marking read/unread
    ])

    calendar_scopes: List[str] = field(default_factory=lambda: [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events.readonly",
    ])

    # Data storage
    data_dir: str = "./data/integrations"

    # Rate limiting
    gmail_requests_per_second: float = 5.0  # Gmail API: 250/user/second
    calendar_requests_per_second: float = 5.0  # Calendar API: 500/user/second

    # Batch settings
    gmail_batch_size: int = 100  # Max messages per batch
    calendar_batch_size: int = 2500  # Max events per request

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    retry_backoff: float = 2.0  # exponential backoff multiplier

    # Timeout
    request_timeout: int = 30  # seconds


@dataclass
class SyncStatus:
    """Sync status tracking"""
    integration_type: IntegrationType
    account_email: str
    last_sync: Optional[datetime] = None
    last_sync_token: Optional[str] = None  # For incremental sync
    total_items_synced: int = 0
    last_error: Optional[str] = None
    is_syncing: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "integration_type": self.integration_type.value,
            "account_email": self.account_email,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "last_sync_token": self.last_sync_token,
            "total_items_synced": self.total_items_synced,
            "last_error": self.last_error,
            "is_syncing": self.is_syncing,
        }


@dataclass
class BatchSyncResult:
    """Result of a batch sync operation"""
    integration_type: IntegrationType
    account_email: str
    start_time: datetime
    end_time: datetime
    items_fetched: int
    items_saved: int
    items_skipped: int
    errors: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()

    @property
    def success_rate(self) -> float:
        total = self.items_fetched
        if total == 0:
            return 0.0
        return (self.items_saved / total) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "integration_type": self.integration_type.value,
            "account_email": self.account_email,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "items_fetched": self.items_fetched,
            "items_saved": self.items_saved,
            "items_skipped": self.items_skipped,
            "success_rate": self.success_rate,
            "errors": self.errors,
        }
