"""
Telegram Bot API Connector
Uses python-telegram-bot library
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

from .base_connector import BaseConnector
from ..models import UnifiedMessage, Platform, MessageType
from ..config import config

try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

class TelegramConnector(BaseConnector):
    platform = Platform.TELEGRAM

    def __init__(self):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.user_id = config.TELEGRAM_USER_ID
        self._message_store: List[UnifiedMessage] = []

        if TELEGRAM_AVAILABLE and self.bot_token:
            self.bot = Bot(token=self.bot_token)
        else:
            self.bot = None

    def is_available(self) -> bool:
        return TELEGRAM_AVAILABLE and bool(self.bot_token)

    def get_user_identifiers(self) -> List[str]:
        return [str(self.user_id)] if self.user_id else []

    def add_update(self, update: dict):
        """Process Telegram update and store message"""
        msg = self._parse_update(update)
        if msg and not self.is_own_message(msg):
            self._message_store.append(msg)

    def fetch_messages(
        self,
        hours_back: int = 24,
        channel_filter: Optional[str] = None
    ) -> List[UnifiedMessage]:
        """Return messages from store within time window"""
        cutoff = datetime.now() - timedelta(hours=hours_back)

        messages = [m for m in self._message_store if m.timestamp >= cutoff]

        if channel_filter:
            messages = [
                m for m in messages
                if channel_filter in (str(m.channel_id), m.channel_name or '')
            ]

        return messages

    def _parse_update(self, update: dict) -> Optional[UnifiedMessage]:
        """Parse Telegram update to UnifiedMessage"""
        try:
            message = update.get("message", {})
            if not message:
                return None

            # Skip non-text messages
            text = message.get("text")
            if not text:
                return None

            # Skip own messages
            from_user = message.get("from", {})
            if from_user.get("id") == self.user_id:
                return None

            chat = message.get("chat", {})
            chat_type = chat.get("type", "private")

            # Determine message type
            if chat_type == "private":
                msg_type = MessageType.DIRECT
            elif chat_type in ("group", "supergroup"):
                msg_type = MessageType.GROUP
            else:
                msg_type = MessageType.CHANNEL

            # Check for mentions
            entities = message.get("entities", [])
            is_mention = any(
                e.get("type") == "mention" or e.get("type") == "text_mention"
                for e in entities
            )

            return UnifiedMessage(
                id=str(message.get("message_id")),
                platform=Platform.TELEGRAM,
                sender_id=str(from_user.get("id")),
                sender_name=f"{from_user.get('first_name', '')} {from_user.get('last_name', '')}".strip() or from_user.get('username', 'Unknown'),
                content=text,
                timestamp=datetime.fromtimestamp(message.get("date", 0)),
                channel_id=str(chat.get("id")),
                channel_name=chat.get("title") or chat.get("username"),
                message_type=msg_type,
                is_mention=is_mention,
                reply_to_id=str(message.get("reply_to_message", {}).get("message_id", "")) or None,
                raw_data=message
            )
        except (KeyError, TypeError):
            return None
