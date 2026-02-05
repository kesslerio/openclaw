"""
Google Calendar Integration
Creates follow-up events from detected commitments
"""
import pickle
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GCAL_AVAILABLE = True
except ImportError:
    GCAL_AVAILABLE = False

from ..models import UnifiedMessage
from ..config import config

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarSync:
    def __init__(self):
        self.service = None
        if GCAL_AVAILABLE:
            try:
                self._initialize()
            except:
                pass

    def _initialize(self):
        """Initialize Google Calendar service"""
        creds = None

        if config.GCAL_TOKEN_PATH.exists():
            with open(config.GCAL_TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not config.GCAL_CREDENTIALS_PATH.exists():
                    return
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(config.GCAL_CREDENTIALS_PATH), SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(config.GCAL_TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def is_available(self) -> bool:
        return GCAL_AVAILABLE and self.service is not None

    def create_commitment_events(
        self,
        messages: List[UnifiedMessage]
    ) -> int:
        """Create calendar events for commitments with deadlines"""

        if not self.is_available():
            return 0

        created = 0

        for msg in messages:
            if not msg.has_commitment or not msg.commitment_deadline:
                continue

            try:
                # Check for conflicts
                if self._has_conflict(msg.commitment_deadline):
                    continue

                event = self._create_event(msg)
                if event:
                    created += 1

            except Exception as e:
                continue

        return created

    def _create_event(self, msg: UnifiedMessage) -> Optional[dict]:
        """Create a single calendar event"""

        event = {
            'summary': f"📱 {msg.commitment_summary or 'Follow-up'}",
            'description': f"""Auto-created from {msg.platform.value}

From: {msg.sender_name}
Original: "{msg.content[:500]}"

---
Created by Universal Briefing""",
            'start': {
                'dateTime': msg.commitment_deadline.isoformat(),
                'timeZone': config.TIMEZONE,
            },
            'end': {
                'dateTime': (msg.commitment_deadline + timedelta(minutes=30)).isoformat(),
                'timeZone': config.TIMEZONE,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 15},
                ],
            },
            'colorId': '6',  # Orange
        }

        result = self.service.events().insert(
            calendarId='primary',
            body=event
        ).execute()

        return result

    def _has_conflict(self, when: datetime, duration_minutes: int = 30) -> bool:
        """Check for calendar conflicts"""

        time_min = when.isoformat() + 'Z'
        time_max = (when + timedelta(minutes=duration_minutes)).isoformat() + 'Z'

        events = self.service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True
        ).execute()

        return len(events.get('items', [])) > 0
