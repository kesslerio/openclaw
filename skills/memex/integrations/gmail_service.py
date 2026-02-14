"""
Gmail Integration Service

Fetches emails from Gmail accounts using Gmail API with OAuth2.
Supports multiple accounts (work and personal).
"""

import base64
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
    EmailData,
    EmailParticipant,
    EmailAttachment,
    IntegrationConfig,
    IntegrationType,
    SyncStatus,
    BatchSyncResult,
)

logger = logging.getLogger(__name__)


class GmailConfig:
    """Gmail-specific configuration"""

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
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
        ]
        self.requests_per_second = requests_per_second


class GmailCredentials:
    """Gmail OAuth2 credentials manager"""

    def __init__(self, config: GmailConfig, account_email: str):
        self.config = config
        self.account_email = account_email
        self.token_path = Path(config.token_dir) / f"gmail_{account_email}.json"
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


class GmailService:
    """Gmail data integration service"""

    def __init__(self, config: Optional[GmailConfig] = None, account_email: str = ""):
        self.config = config or GmailConfig()
        self.account_email = account_email
        self.credentials_manager = GmailCredentials(self.config, account_email)
        self.service = None
        self._last_request_time = 0.0

    def connect(self):
        """Connect to Gmail API"""
        credentials = self.credentials_manager.get_credentials()
        self.service = build("gmail", "v1", credentials=credentials)
        logger.info(f"✅ Connected to Gmail API for {self.account_email}")

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

    def list_messages(
        self,
        query: str = "",
        max_results: int = 100,
        label_ids: Optional[List[str]] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List messages matching criteria

        Args:
            query: Gmail search query (e.g., "after:2026/01/01")
            max_results: Max messages to return
            label_ids: Filter by label IDs
            page_token: Pagination token

        Returns:
            Dict with 'messages' list and optional 'nextPageToken'
        """
        self._rate_limit()

        try:
            request_params = {"userId": "me", "maxResults": max_results}

            if query:
                request_params["q"] = query
            if label_ids:
                request_params["labelIds"] = label_ids
            if page_token:
                request_params["pageToken"] = page_token

            result = self.service.users().messages().list(**request_params).execute()

            return result

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            raise

    def get_message(self, message_id: str, format: str = "full") -> Dict[str, Any]:
        """
        Get full message details

        Args:
            message_id: Message ID
            format: full, metadata, minimal, raw

        Returns:
            Full message data
        """
        self._rate_limit()

        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format=format)
                .execute()
            )
            return message

        except HttpError as error:
            logger.error(f"Error fetching message {message_id}: {error}")
            raise

    def parse_message(self, raw_message: Dict[str, Any]) -> EmailData:
        """Parse raw Gmail API message to EmailData"""
        payload = raw_message.get("payload", {})
        headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}

        # Parse participants
        from_header = headers.get("from", "")
        from_participant = self._parse_email_address(from_header)

        to_participants = []
        to_header = headers.get("to", "")
        if to_header:
            to_participants = [
                self._parse_email_address(addr)
                for addr in to_header.split(",")
            ]

        cc_participants = []
        cc_header = headers.get("cc", "")
        if cc_header:
            cc_participants = [
                self._parse_email_address(addr)
                for addr in cc_header.split(",")
            ]

        # Parse date
        date_str = headers.get("date", "")
        date = self._parse_date(date_str) if date_str else datetime.now()

        # Extract body
        body_text, body_html = self._extract_body(payload)

        # Extract attachments
        attachments = self._extract_attachments(payload)

        # Labels
        labels = raw_message.get("labelIds", [])

        # Read status
        is_read = "UNREAD" not in labels
        is_starred = "STARRED" in labels

        return EmailData(
            message_id=raw_message["id"],
            thread_id=raw_message["threadId"],
            subject=headers.get("subject", "(No Subject)"),
            from_=from_participant,
            to=to_participants,
            cc=cc_participants,
            date=date,
            body_text=body_text,
            body_html=body_html,
            labels=labels,
            attachments=attachments,
            is_read=is_read,
            is_starred=is_starred,
            account_email=self.account_email,
            raw_headers=headers,
        )

    def fetch_emails(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_emails: int = 500,
        query: str = "",
    ) -> List[EmailData]:
        """
        Fetch emails within date range

        Args:
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: now)
            max_emails: Maximum emails to fetch
            query: Additional Gmail search query

        Returns:
            List of parsed emails
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()

        # Build query
        date_query = f"after:{start_date.strftime('%Y/%m/%d')} before:{end_date.strftime('%Y/%m/%d')}"
        full_query = f"{date_query} {query}".strip()

        logger.info(
            f"Fetching emails for {self.account_email}: {full_query} (max {max_emails})"
        )

        emails = []
        page_token = None
        fetched = 0

        while fetched < max_emails:
            batch_size = min(100, max_emails - fetched)

            # List messages
            result = self.list_messages(
                query=full_query,
                max_results=batch_size,
                page_token=page_token,
            )

            messages = result.get("messages", [])
            if not messages:
                break

            # Fetch full message details
            for msg_summary in messages:
                try:
                    full_message = self.get_message(msg_summary["id"])
                    email_data = self.parse_message(full_message)
                    emails.append(email_data)
                    fetched += 1

                except Exception as e:
                    logger.error(
                        f"Error parsing message {msg_summary['id']}: {e}"
                    )
                    continue

            # Check for next page
            page_token = result.get("nextPageToken")
            if not page_token:
                break

            logger.info(f"Fetched {fetched}/{max_emails} emails...")

        logger.info(f"✅ Fetched {len(emails)} emails for {self.account_email}")
        return emails

    def batch_export(
        self,
        output_dir: Path,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_emails: int = 1000,
    ) -> BatchSyncResult:
        """
        Export emails to JSON files

        Args:
            output_dir: Output directory
            start_date: Start date
            end_date: End date
            max_emails: Maximum emails to export

        Returns:
            Batch sync result
        """
        start_time = datetime.now()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting batch export to {output_dir}")

        # Fetch emails
        emails = self.fetch_emails(start_date, end_date, max_emails)

        # Save to JSON files (organized by date)
        saved = 0
        errors = []

        for email in emails:
            try:
                # Create date-based subdirectory
                date_dir = output_dir / email.date.strftime("%Y-%m-%d")
                date_dir.mkdir(parents=True, exist_ok=True)

                # Save email
                filename = date_dir / f"email_{email.message_id}.json"
                with open(filename, "w") as f:
                    json.dump(email.to_dict(), f, indent=2)

                saved += 1

            except Exception as e:
                error_msg = f"Error saving email {email.message_id}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Create manifest
        manifest_file = output_dir / "manifest.json"
        manifest = {
            "account_email": self.account_email,
            "export_time": start_time.isoformat(),
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "total_emails": len(emails),
            "emails_saved": saved,
            "errors": len(errors),
        }

        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        end_time = datetime.now()

        result = BatchSyncResult(
            integration_type=IntegrationType.GMAIL,
            account_email=self.account_email,
            start_time=start_time,
            end_time=end_time,
            items_fetched=len(emails),
            items_saved=saved,
            items_skipped=len(emails) - saved,
            errors=errors,
        )

        logger.info(
            f"✅ Batch export complete: {saved}/{len(emails)} emails saved "
            f"in {result.duration_seconds:.1f}s"
        )

        return result

    @staticmethod
    def _parse_email_address(address_str: str) -> EmailParticipant:
        """Parse email address from header"""
        address_str = address_str.strip()

        # Format: "Name <email@example.com>" or just "email@example.com"
        if "<" in address_str and ">" in address_str:
            name = address_str[: address_str.index("<")].strip().strip('"')
            email = address_str[address_str.index("<") + 1 : address_str.index(">")]
            return EmailParticipant(email=email, name=name if name else None)
        else:
            return EmailParticipant(email=address_str)

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse RFC 2822 date string"""
        from email.utils import parsedate_to_datetime

        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.now()

    @staticmethod
    def _extract_body(payload: Dict[str, Any]) -> tuple[str, str]:
        """Extract text and HTML body from message payload"""
        body_text = ""
        body_html = ""

        if "body" in payload and "data" in payload["body"]:
            # Simple message
            data = payload["body"]["data"]
            decoded = base64.urlsafe_b64decode(data).decode("utf-8")

            mime_type = payload.get("mimeType", "")
            if "html" in mime_type:
                body_html = decoded
            else:
                body_text = decoded

        elif "parts" in payload:
            # Multipart message
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")

                if "data" in part.get("body", {}):
                    data = part["body"]["data"]
                    decoded = base64.urlsafe_b64decode(data).decode("utf-8")

                    if mime_type == "text/plain":
                        body_text = decoded
                    elif mime_type == "text/html":
                        body_html = decoded

        return body_text, body_html

    @staticmethod
    def _extract_attachments(payload: Dict[str, Any]) -> List[EmailAttachment]:
        """Extract attachment metadata"""
        attachments = []

        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("filename"):
                    attachment = EmailAttachment(
                        filename=part["filename"],
                        mime_type=part.get("mimeType", "application/octet-stream"),
                        size_bytes=part.get("body", {}).get("size", 0),
                        attachment_id=part.get("body", {}).get("attachmentId"),
                    )
                    attachments.append(attachment)

        return attachments
