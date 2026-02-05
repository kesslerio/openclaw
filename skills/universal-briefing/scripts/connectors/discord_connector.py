"""
Discord Bot API Connector
Uses discord.py library
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional

from .base_connector import BaseConnector
from ..models import UnifiedMessage, Platform, MessageType
from ..config import config

try:
    import discord
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

class DiscordConnector(BaseConnector):
    platform = Platform.DISCORD

    def __init__(self):
        self.bot_token = config.DISCORD_BOT_TOKEN
        self.user_id = config.DISCORD_USER_ID
        self._message_store: List[UnifiedMessage] = []

    def is_available(self) -> bool:
        return DISCORD_AVAILABLE and bool(self.bot_token)

    def get_user_identifiers(self) -> List[str]:
        return [str(self.user_id)] if self.user_id else []

    def add_message(self, message_data: dict):
        """Add message from Discord event"""
        msg = self._parse_message(message_data)
        if msg and not self.is_own_message(msg):
            self._message_store.append(msg)

    def fetch_messages(
        self,
        hours_back: int = 24,
        channel_filter: Optional[str] = None
    ) -> List[UnifiedMessage]:
        """Return stored messages within time window"""
        cutoff = datetime.now() - timedelta(hours=hours_back)

        messages = [m for m in self._message_store if m.timestamp >= cutoff]

        if channel_filter:
            messages = [
                m for m in messages
                if channel_filter in (str(m.channel_id), m.channel_name or '')
            ]

        return messages

    def _parse_message(self, data: dict) -> Optional[UnifiedMessage]:
        """Parse Discord message to UnifiedMessage"""
        try:
            # Skip bot messages
            if data.get("author", {}).get("bot"):
                return None

            # Skip system messages
            msg_type_id = data.get("type", 0)
            if msg_type_id != 0:  # 0 = DEFAULT
                return None

            author = data.get("author", {})
            channel = data.get("channel", {})

            # Determine message type
            channel_type = channel.get("type", 0)
            if channel_type == 1:  # DM
                msg_type = MessageType.DIRECT
            elif channel_type in [0, 2, 5]:  # Guild text/voice/news
                msg_type = MessageType.CHANNEL
            else:
                msg_type = MessageType.GROUP

            # Check for mentions
            mentions = data.get("mentions", [])
            is_mention = any(m.get("id") == str(self.user_id) for m in mentions)

            return UnifiedMessage(
                id=data.get("id"),
                platform=Platform.DISCORD,
                sender_id=author.get("id"),
                sender_name=author.get("username", "Unknown"),
                content=data.get("content", ""),
                timestamp=datetime.fromisoformat(data.get("timestamp", "").replace("Z", "+00:00")),
                channel_id=str(channel.get("id")),
                channel_name=channel.get("name"),
                message_type=msg_type,
                is_mention=is_mention,
                has_attachment=bool(data.get("attachments")),
                raw_data=data
            )
        except (KeyError, TypeError, ValueError):
            return None
