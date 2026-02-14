"""
Google Calendar Integration Service

Fetches calendar events using Calendar API with OAuth2.
Supports multiple accounts (work and personal).
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import (
    CalendarEvent,
    CalendarAttendee,
    IntegrationConfig,
    IntegrationType,
    SyncStatus,
    BatchSyncResult,
)

logger = logging.getLogger(__name__)


class CalendarConfig:
    """Calendar-specific configuration"""

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_dir: str = ".tokens",
        scopes: Optional[List[str]] = None,
        requests_per_second: float = 5.0,
    ):
        self.credentials_path = credentials_path
        self.token_dir = token_dir
        self.scopes = scopes or [
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events.readonly",
        ]
        self.requests_per_second = requests_per_second


class CalendarCredentials:
    """Calendar OAuth2 credentials manager"""

    def __init__(self, config: CalendarConfig, account_email: str):
        self.config = config
        self.account_email = account_email
        self.token_path = Path(config.token_dir) / f"calendar_{account_email}.json"
        self.credentials: Optional[Credentials] = None

    def get_credentials(self) -> Credentials:
        """Get valid credentials, refreshing if needed"""
        if self.credentials and self.credentials.valid:
            return self.credentials

        # Load existing token
        if self.token_path.exists():
            self.credentials = Credentials.from_authorized_user_file(
                str(self.token_path), self.config.scopes
            )

        # Refresh if expired
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
            self._save_credentials()
            return self.credentials

        # Need new authorization
        if not self.credentials or not self.credentials.valid:
            raise ValueError(
                f"No valid credentials for {self.account_email}. "
                f"Run auth flow first using authorize() method."
            )

        return self.credentials

    def authorize(self) -> Credentials:
        """Run OAuth2 authorization flow"""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.config.credentials_path, self.config.scopes
        )

        # Use local server flow (opens browser)
        self.credentials = flow.run_local_server(port=0)
        self._save_credentials()

        logger.info(f"✅ Authorized {self.account_email}")
        return self.credentials

    def _save_credentials(self):
        """Save credentials to token file"""
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.token_path, "w") as f:
            f.write(self.credentials.to_json())


class CalendarService:
    """Google Calendar data integration service"""

    def __init__(self, config: Optional[CalendarConfig] = None, account_email: str = ""):
        self.config = config or CalendarConfig()
        self.account_email = account_email
        self.credentials_manager = CalendarCredentials(self.config, account_email)
        self.service = None
        self._last_request_time = 0.0

    def connect(self):
        """Connect to Calendar API"""
        credentials = self.credentials_manager.get_credentials()
        self.service = build("calendar", "v3", credentials=credentials)
        logger.info(f"✅ Connected to Calendar API for {self.account_email}")

    def authorize(self):
        """Run OAuth2 authorization flow"""
        self.credentials_manager.authorize()
        self.connect()

    def _rate_limit(self):
        """Rate limiting between requests"""
        elapsed = time.time() - self._last_request_time
        min_interval = 1.0 / self.config.requests_per_second

        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        self._last_request_time = time.time()

    def list_calendars(self) -> List[Dict[str, Any]]:
        """List all calendars for the account"""
        self._rate_limit()

        try:
            calendar_list = self.service.calendarList().list().execute()
            return calendar_list.get("items", [])

        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            raise

    def list_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 2500,
        single_events: bool = True,
        order_by: str = "startTime",
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List events from calendar

        Args:
            calendar_id: Calendar ID (default: primary)
            time_min: Start time (RFC3339)
            time_max: End time (RFC3339)
            max_results: Max events to return
            single_events: Expand recurring events to instances
            order_by: Sort order (startTime, updated)
            page_token: Pagination token

        Returns:
            Dict with 'items' list and optional 'nextPageToken'
        """
        self._rate_limit()

        try:
            request_params = {
                "calendarId": calendar_id,
                "maxResults": max_results,
                "singleEvents": single_events,
            }

            if time_min:
                request_params["timeMin"] = time_min.isoformat() + "Z"
            if time_max:
                request_params["timeMax"] = time_max.isoformat() + "Z"
            if single_events and order_by:
                request_params["orderBy"] = order_by
            if page_token:
                request_params["pageToken"] = page_token

            events = self.service.events().list(**request_params).execute()
            return events

        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            raise

    def parse_event(self, raw_event: Dict[str, Any], calendar_id: str) -> CalendarEvent:
        """Parse raw Calendar API event to CalendarEvent"""

        # Parse start/end times
        start_data = raw_event.get("start", {})
        end_data = raw_event.get("end", {})

        all_day = "date" in start_data  # All-day events use 'date' not 'dateTime'

        if all_day:
            start = datetime.fromisoformat(start_data["date"])
            end = datetime.fromisoformat(end_data["date"])
        else:
            start_str = start_data.get("dateTime", "")
            end_str = end_data.get("dateTime", "")

            start = self._parse_datetime(start_str) if start_str else datetime.now()
            end = self._parse_datetime(end_str) if end_str else datetime.now()

        # Parse attendees
        attendees = []
        for att_data in raw_event.get("attendees", []):
            attendee = CalendarAttendee(
                email=att_data.get("email", ""),
                name=att_data.get("displayName"),
                response_status=att_data.get("responseStatus"),
                is_organizer=att_data.get("organizer", False),
                is_optional=att_data.get("optional", False),
            )
            attendees.append(attendee)

        # Parse organizer
        organizer_data = raw_event.get("organizer", {})
        organizer = None
        if organizer_data:
            organizer = CalendarAttendee(
                email=organizer_data.get("email", ""),
                name=organizer_data.get("displayName"),
                is_organizer=True,
            )

        # Conference links
        conference_data = raw_event.get("conferenceData", {})
        hangout_link = raw_event.get("hangoutLink")
        meet_link = None

        for entry_point in conference_data.get("entryPoints", []):
            if entry_point.get("entryPointType") == "video":
                meet_link = entry_point.get("uri")
                break

        # Parse timestamps
        created = self._parse_datetime(raw_event.get("created", ""))
        updated = self._parse_datetime(raw_event.get("updated", ""))

        return CalendarEvent(
            event_id=raw_event["id"],
            calendar_id=calendar_id,
            summary=raw_event.get("summary", "(No Title)"),
            description=raw_event.get("description", ""),
            location=raw_event.get("location", ""),
            start=start,
            end=end,
            all_day=all_day,
            attendees=attendees,
            organizer=organizer,
            status=raw_event.get("status", "confirmed"),
            visibility=raw_event.get("visibility", "default"),
            recurrence=raw_event.get("recurrence"),
            recurring_event_id=raw_event.get("recurringEventId"),
            hangout_link=hangout_link,
            meet_link=meet_link,
            created=created,
            updated=updated,
            account_email=self.account_email,
            raw_data=raw_event,
        )

    def fetch_events(
        self,
        calendar_id: str = "primary",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_events: int = 2500,
    ) -> List[CalendarEvent]:
        """
        Fetch events within date range

        Args:
            calendar_id: Calendar ID (default: primary)
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: now)
            max_events: Maximum events to fetch

        Returns:
            List of parsed events
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()

        logger.info(
            f"Fetching events for {self.account_email} from {start_date.date()} to {end_date.date()}"
        )

        events = []
        page_token = None
        fetched = 0

        while fetched < max_events:
            batch_size = min(2500, max_events - fetched)

            # List events
            result = self.list_events(
                calendar_id=calendar_id,
                time_min=start_date,
                time_max=end_date,
                max_results=batch_size,
                page_token=page_token,
            )

            items = result.get("items", [])
            if not items:
                break

            # Parse events
            for raw_event in items:
                try:
                    event = self.parse_event(raw_event, calendar_id)
                    events.append(event)
                    fetched += 1

                except Exception as e:
                    logger.error(f"Error parsing event {raw_event.get('id')}: {e}")
                    continue

            # Check for next page
            page_token = result.get("nextPageToken")
            if not page_token:
                break

            logger.info(f"Fetched {fetched}/{max_events} events...")

        logger.info(f"✅ Fetched {len(events)} events for {self.account_email}")
        return events

    def batch_export(
        self,
        output_dir: Path,
        calendar_id: str = "primary",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_events: int = 2500,
    ) -> BatchSyncResult:
        """
        Export events to JSON files

        Args:
            output_dir: Output directory
            calendar_id: Calendar ID
            start_date: Start date
            end_date: End date
            max_events: Maximum events to export

        Returns:
            Batch sync result
        """
        start_time = datetime.now()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting batch export to {output_dir}")

        # Fetch events
        events = self.fetch_events(calendar_id, start_date, end_date, max_events)

        # Save to JSON files (organized by date)
        saved = 0
        errors = []

        for event in events:
            try:
                # Create date-based subdirectory
                date_dir = output_dir / event.start.strftime("%Y-%m-%d")
                date_dir.mkdir(parents=True, exist_ok=True)

                # Save event
                filename = date_dir / f"event_{event.event_id}.json"
                with open(filename, "w") as f:
                    json.dump(event.to_dict(), f, indent=2)

                saved += 1

            except Exception as e:
                error_msg = f"Error saving event {event.event_id}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Create manifest
        manifest_file = output_dir / "manifest.json"
        manifest = {
            "account_email": self.account_email,
            "calendar_id": calendar_id,
            "export_time": start_time.isoformat(),
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "total_events": len(events),
            "events_saved": saved,
            "errors": len(errors),
        }

        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        end_time = datetime.now()

        result = BatchSyncResult(
            integration_type=IntegrationType.CALENDAR,
            account_email=self.account_email,
            start_time=start_time,
            end_time=end_time,
            items_fetched=len(events),
            items_saved=saved,
            items_skipped=len(events) - saved,
            errors=errors,
        )

        logger.info(
            f"✅ Batch export complete: {saved}/{len(events)} events saved "
            f"in {result.duration_seconds:.1f}s"
        )

        return result

    @staticmethod
    def _parse_datetime(datetime_str: str) -> Optional[datetime]:
        """Parse ISO 8601 datetime string"""
        if not datetime_str:
            return None

        try:
            # Handle timezone
            if "Z" in datetime_str:
                datetime_str = datetime_str.replace("Z", "+00:00")

            return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

        except Exception as e:
            logger.error(f"Error parsing datetime '{datetime_str}': {e}")
            return None
