"""
WhatsApp Business Cloud API Connector
For personal use, requires Business API access or third-party bridge
"""
import requests
from datetime import datetime, timedelta
from typing import List, Optional
import json

from .base_connector import BaseConnector
from ..models import UnifiedMessage, Platform, MessageType
from ..config import config

class WhatsAppConnector(BaseConnector):
    platform = Platform.WHATSAPP

    def __init__(self):
        self.access_token = config.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = config.WHATSAPP_PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        # In-memory message store (populated via webhook)
        self._message_store: List[UnifiedMessage] = []

    def is_available(self) -> bool:
        return bool(self.access_token and self.phone_number_id)

    def get_user_identifiers(self) -> List[str]:
        return config.USER_PHONE_NUMBERS

    def add_webhook_message(self, webhook_data: dict):
        """Process incoming webhook and store message"""
        msg = self._parse_webhook(webhook_data)
        if msg and not self.is_own_message(msg):
            self._message_store.append(msg)

    def fetch_messages(
        self,
        hours_back: int = 24,
        channel_filter: Optional[str] = None
    ) -> List[UnifiedMessage]:
        """
        Return messages from in-memory store within time window.
        WhatsApp API doesn't support historical message retrieval,
        so this relies on webhook collection.
        """
        cutoff = datetime.now() - timedelta(hours=hours_back)

        messages = [
            m for m in self._message_store
            if m.timestamp >= cutoff
        ]

        if channel_filter:
            messages = [m for m in messages if channel_filter in (m.sender_id, m.channel_id or '')]

        return messages

    def _parse_webhook(self, data: dict) -> Optional[UnifiedMessage]:
        """Parse WhatsApp webhook payload"""
        try:
            entry = data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})

            messages = value.get("messages", [])
            if not messages:
                return None

            msg = messages[0]
            msg_type = msg.get("type")

            # Skip non-text messages for now
            if msg_type != "text":
                return None

            contacts = value.get("contacts", [{}])[0]

            # Detect group
            is_group = "group" in str(msg.get("from", "")).lower()

            return UnifiedMessage(
                id=msg.get("id"),
                platform=Platform.WHATSAPP,
                sender_id=msg.get("from"),
                sender_name=contacts.get("profile", {}).get("name", msg.get("from")),
                content=msg.get("text", {}).get("body", ""),
                timestamp=datetime.fromtimestamp(int(msg.get("timestamp", 0))),
                message_type=MessageType.GROUP if is_group else MessageType.DIRECT,
                raw_data=msg
            )
        except (KeyError, IndexError, TypeError):
            return None
