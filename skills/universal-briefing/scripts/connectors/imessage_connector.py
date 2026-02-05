"""
iMessage Connector for macOS
Reads from local chat.db SQLite database
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from .base_connector import BaseConnector
from ..models import UnifiedMessage, Platform, MessageType
from ..config import config

class iMessageConnector(BaseConnector):
    platform = Platform.IMESSAGE

    def __init__(self):
        self.db_path = config.IMESSAGE_DB_PATH

    def is_available(self) -> bool:
        return self.db_path.exists()

    def get_user_identifiers(self) -> List[str]:
        return config.USER_PHONE_NUMBERS + config.USER_EMAILS

    def fetch_messages(
        self,
        hours_back: int = 24,
        channel_filter: Optional[str] = None
    ) -> List[UnifiedMessage]:
        """Fetch messages from iMessage database"""
        messages = []

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Apple timestamp: nanoseconds since 2001-01-01
            apple_epoch = datetime(2001, 1, 1)
            cutoff = datetime.now() - timedelta(hours=hours_back)
            cutoff_ns = int((cutoff - apple_epoch).total_seconds() * 1e9)

            query = """
            SELECT
                m.ROWID,
                m.guid,
                h.id as sender_id,
                m.text,
                m.date,
                m.is_from_me,
                m.service,
                c.chat_identifier,
                c.display_name,
                c.group_id,
                m.cache_has_attachments
            FROM message m
            LEFT JOIN handle h ON m.handle_id = h.ROWID
            LEFT JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
            LEFT JOIN chat c ON cmj.chat_id = c.ROWID
            WHERE m.date > ?
            AND m.text IS NOT NULL
            AND m.text != ''
            ORDER BY m.date DESC
            """

            cursor.execute(query, (cutoff_ns,))

            for row in cursor.fetchall():
                (rowid, guid, sender_id, text, date_ns, is_from_me,
                 service, chat_id, display_name, group_id, has_attach) = row

                # Skip own messages
                if is_from_me:
                    continue

                # Filter by channel if specified
                if channel_filter and channel_filter not in (sender_id or '', chat_id or ''):
                    continue

                timestamp = apple_epoch + timedelta(seconds=date_ns / 1e9)

                # Determine message type
                is_group = bool(group_id) or (chat_id and 'chat' in str(chat_id).lower())

                messages.append(UnifiedMessage(
                    id=guid or str(rowid),
                    platform=Platform.IMESSAGE,
                    sender_id=sender_id or 'unknown',
                    sender_name=sender_id or 'Unknown',  # iMessage doesn't store names
                    content=text,
                    timestamp=timestamp,
                    channel_id=chat_id,
                    channel_name=display_name or chat_id,
                    message_type=MessageType.GROUP if is_group else MessageType.DIRECT,
                    has_attachment=bool(has_attach),
                    raw_data={'service': service, 'group_id': group_id}
                ))

            conn.close()

        except Exception as e:
            print(f"iMessage fetch error: {e}")

        return messages
