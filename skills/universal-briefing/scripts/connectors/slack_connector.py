"""
Slack API Connector
Uses Slack Web API with Bot Token
"""
import requests
from datetime import datetime, timedelta
from typing import List, Optional

from .base_connector import BaseConnector
from ..models import UnifiedMessage, Platform, MessageType
from ..config import config

class SlackConnector(BaseConnector):
    platform = Platform.SLACK

    def __init__(self):
        self.bot_token = config.SLACK_BOT_TOKEN
        self.user_id = config.SLACK_USER_ID
        self.headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        self._channel_cache = {}
        self._user_cache = {}

    def is_available(self) -> bool:
        if not self.bot_token:
            return False
        try:
            resp = requests.post(
                "https://slack.com/api/auth.test",
                headers=self.headers
            )
            return resp.json().get("ok", False)
        except:
            return False

    def get_user_identifiers(self) -> List[str]:
        return [self.user_id] if self.user_id else []

    def fetch_messages(
        self,
        hours_back: int = 24,
        channel_filter: Optional[str] = None
    ) -> List[UnifiedMessage]:
        """Fetch messages from Slack channels and DMs"""
        messages = []
        oldest = (datetime.now() - timedelta(hours=hours_back)).timestamp()

        # Get channels the bot is in
        channels = self._get_channels()

        for channel in channels:
            if channel_filter and channel['id'] != channel_filter:
                continue

            try:
                resp = requests.post(
                    "https://slack.com/api/conversations.history",
                    headers=self.headers,
                    json={
                        "channel": channel['id'],
                        "oldest": str(oldest),
                        "limit": 100
                    }
                )
                data = resp.json()

                if not data.get("ok"):
                    continue

                for msg in data.get("messages", []):
                    unified = self._parse_message(msg, channel)
                    if unified and not self.is_own_message(unified):
                        messages.append(unified)

            except Exception as e:
                continue

        return messages

    def _get_channels(self) -> List[dict]:
        """Get list of channels bot is member of"""
        channels = []

        try:
            # Public channels
            resp = requests.post(
                "https://slack.com/api/conversations.list",
                headers=self.headers,
                json={"types": "public_channel,private_channel,mpim,im", "limit": 100}
            )
            data = resp.json()

            if data.get("ok"):
                for ch in data.get("channels", []):
                    if ch.get("is_member", True):  # Include DMs
                        channels.append({
                            'id': ch['id'],
                            'name': ch.get('name', ch['id']),
                            'is_im': ch.get('is_im', False),
                            'is_group': ch.get('is_mpim', False) or ch.get('is_group', False)
                        })
        except:
            pass

        return channels

    def _parse_message(self, msg: dict, channel: dict) -> Optional[UnifiedMessage]:
        """Parse Slack message to UnifiedMessage"""
        # Skip bot messages and system messages
        if msg.get("subtype") in ["bot_message", "channel_join", "channel_leave", "file_share"]:
            return None

        user_id = msg.get("user")
        if not user_id:
            return None

        # Get user info
        user_name = self._get_user_name(user_id)

        # Determine message type
        if channel.get('is_im'):
            msg_type = MessageType.DIRECT
        elif channel.get('is_group'):
            msg_type = MessageType.GROUP
        else:
            msg_type = MessageType.CHANNEL

        # Check for mentions
        text = msg.get("text", "")
        is_mention = f"<@{self.user_id}>" in text if self.user_id else False

        # Clean up mention formatting
        text = self._clean_text(text)

        return UnifiedMessage(
            id=msg.get("ts"),
            platform=Platform.SLACK,
            sender_id=user_id,
            sender_name=user_name,
            content=text,
            timestamp=datetime.fromtimestamp(float(msg.get("ts", 0))),
            channel_id=channel['id'],
            channel_name=channel['name'],
            message_type=msg_type,
            thread_id=msg.get("thread_ts"),
            is_mention=is_mention,
            has_attachment=bool(msg.get("files")),
            raw_data=msg
        )

    def _get_user_name(self, user_id: str) -> str:
        """Get user display name from cache or API"""
        if user_id in self._user_cache:
            return self._user_cache[user_id]

        try:
            resp = requests.post(
                "https://slack.com/api/users.info",
                headers=self.headers,
                json={"user": user_id}
            )
            data = resp.json()

            if data.get("ok"):
                user = data.get("user", {})
                name = user.get("real_name") or user.get("name", user_id)
                self._user_cache[user_id] = name
                return name
        except:
            pass

        return user_id

    def _clean_text(self, text: str) -> str:
        """Clean Slack formatting from text"""
        import re
        # Replace user mentions with names
        def replace_mention(match):
            uid = match.group(1)
            return f"@{self._get_user_name(uid)}"

        text = re.sub(r'<@(\w+)>', replace_mention, text)
        # Remove channel links
        text = re.sub(r'<#\w+\|(\w+)>', r'#\1', text)
        # Remove URL formatting
        text = re.sub(r'<(https?://[^|>]+)\|?[^>]*>', r'\1', text)

        return text
