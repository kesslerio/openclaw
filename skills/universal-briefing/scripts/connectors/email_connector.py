"""
Gmail/Email Connector
Uses Gmail API for full access
"""
import pickle
import base64
import email
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

from .base_connector import BaseConnector
from ..models import UnifiedMessage, Platform, MessageType
from ..config import config

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class EmailConnector(BaseConnector):
    platform = Platform.EMAIL

    def __init__(self):
        self.service = None
        self.user_email = None
        if GMAIL_AVAILABLE:
            try:
                self._initialize()
            except:
                pass

    def _initialize(self):
        """Initialize Gmail API service"""
        creds = None

        if config.GMAIL_TOKEN_PATH.exists():
            with open(config.GMAIL_TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not config.GMAIL_CREDENTIALS_PATH.exists():
                    return
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(config.GMAIL_CREDENTIALS_PATH), SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(config.GMAIL_TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

        # Get user's email
        profile = self.service.users().getProfile(userId='me').execute()
        self.user_email = profile.get('emailAddress', '')

    def is_available(self) -> bool:
        return GMAIL_AVAILABLE and self.service is not None

    def get_user_identifiers(self) -> List[str]:
        ids = [self.user_email] if self.user_email else []
        ids.extend(config.USER_EMAILS)
        return [e for e in ids if e]

    def fetch_messages(
        self,
        hours_back: int = 24,
        channel_filter: Optional[str] = None
    ) -> List[UnifiedMessage]:
        """Fetch emails from Gmail"""
        messages = []

        # Build query
        after_date = (datetime.now() - timedelta(hours=hours_back)).strftime('%Y/%m/%d')
        query = f"after:{after_date}"

        if channel_filter:
            query += f" from:{channel_filter}"

        # Exclude sent mail
        query += " -in:sent"

        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()

            message_ids = results.get('messages', [])

            for msg_ref in message_ids:
                try:
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=msg_ref['id'],
                        format='full'
                    ).execute()

                    unified = self._parse_email(msg)
                    if unified:
                        messages.append(unified)
                except Exception as e:
                    continue

        except Exception as e:
            print(f"Email fetch error: {e}")

        return messages

    def _parse_email(self, msg: dict) -> Optional[UnifiedMessage]:
        """Parse Gmail API message to UnifiedMessage"""
        headers = {h['name'].lower(): h['value'] for h in msg['payload']['headers']}

        # Extract sender
        from_header = headers.get('from', '')
        sender_name, sender_email = self._parse_from_header(from_header)

        # Skip own messages
        if sender_email in self.get_user_identifiers():
            return None

        # Extract body
        body = self._extract_body(msg['payload'])
        if not body:
            return None

        # Parse timestamp
        internal_date = int(msg.get('internalDate', 0)) / 1000
        timestamp = datetime.fromtimestamp(internal_date)

        # Check for mentions
        to_header = headers.get('to', '') + headers.get('cc', '')
        is_mention = any(e in to_header for e in self.get_user_identifiers())

        # Check attachments
        has_attachment = bool(msg['payload'].get('parts', []))

        return UnifiedMessage(
            id=msg['id'],
            platform=Platform.EMAIL,
            sender_id=sender_email,
            sender_name=sender_name or sender_email,
            content=body[:5000],  # Truncate very long emails
            timestamp=timestamp,
            channel_name=headers.get('subject', 'No Subject'),
            message_type=MessageType.DIRECT,
            thread_id=msg.get('threadId'),
            is_mention=is_mention,
            has_attachment=has_attachment,
            raw_data={'headers': headers, 'labels': msg.get('labelIds', [])}
        )

    def _parse_from_header(self, from_header: str) -> tuple:
        """Parse 'Name <email@domain.com>' format"""
        import re
        match = re.match(r'^"?([^"<]*)"?\s*<?([^>]*)>?', from_header)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return '', from_header

    def _extract_body(self, payload: dict) -> str:
        """Extract plain text body from email payload"""
        if payload.get('body', {}).get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')

        for part in payload.get('parts', []):
            if part.get('mimeType') == 'text/plain':
                if part.get('body', {}).get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            elif part.get('parts'):
                result = self._extract_body(part)
                if result:
                    return result

        return ''
