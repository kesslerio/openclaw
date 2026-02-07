"""
SQLite storage for Universal Briefing messages.
Provides persistence for platforms without historical APIs.
Signed-off-by: codex_nike
"""
from __future__ import annotations

import json
import shutil
import sqlite3
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional

from .models import UnifiedMessage, Platform, MessageType, Classification
from .config import config
from .constants import DB_TIMEOUT, DB_BUSY_TIMEOUT, MAX_BACKUPS
from .logging_config import get_logger

logger = get_logger("storage")

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
  id TEXT NOT NULL,
  platform TEXT NOT NULL,
  sender_id TEXT NOT NULL,
  sender_name TEXT NOT NULL,
  content TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  channel_id TEXT,
  channel_name TEXT,
  message_type TEXT NOT NULL,
  thread_id TEXT,
  reply_to_id TEXT,
  is_mention INTEGER NOT NULL DEFAULT 0,
  has_attachment INTEGER NOT NULL DEFAULT 0,
  attachment_type TEXT,
  raw_data TEXT,
  ingest_ts TEXT NOT NULL,
  read INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (platform, id)
);
CREATE INDEX IF NOT EXISTS idx_messages_platform_timestamp
  ON messages(platform, timestamp);
"""

FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
  sender_name,
  channel_name,
  content,
  content='messages',
  content_rowid='rowid'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
  INSERT INTO messages_fts(rowid, sender_name, channel_name, content)
  VALUES (new.rowid, new.sender_name, COALESCE(new.channel_name, ''), new.content);
END;

CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
  INSERT INTO messages_fts(messages_fts, rowid, sender_name, channel_name, content)
  VALUES ('delete', old.rowid, old.sender_name, COALESCE(old.channel_name, ''), old.content);
END;

CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON messages BEGIN
  INSERT INTO messages_fts(messages_fts, rowid, sender_name, channel_name, content)
  VALUES ('delete', old.rowid, old.sender_name, COALESCE(old.channel_name, ''), old.content);
  INSERT INTO messages_fts(rowid, sender_name, channel_name, content)
  VALUES (new.rowid, new.sender_name, COALESCE(new.channel_name, ''), new.content);
END;
"""


def _connect(path: Path) -> sqlite3.Connection:
    """Create a connection with standard settings."""
    conn = sqlite3.connect(str(path), timeout=DB_TIMEOUT)
    conn.execute(f"PRAGMA busy_timeout={DB_BUSY_TIMEOUT}")
    return conn


def _ensure_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(path) as conn:
        conn.executescript(SCHEMA)
        # Enable WAL mode for concurrent reads
        conn.execute("PRAGMA journal_mode=WAL")
        # Add read column if missing (migration)
        try:
            conn.execute("SELECT read FROM messages LIMIT 0")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE messages ADD COLUMN read INTEGER NOT NULL DEFAULT 0")
            logger.info("Migrated: added 'read' column to messages table")
        # Set up FTS5
        try:
            conn.executescript(FTS_SCHEMA)
            # Rebuild FTS index from existing data if table was just created
            existing = conn.execute(
                "SELECT COUNT(*) FROM messages_fts"
            ).fetchone()[0]
            total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            if total > 0 and existing == 0:
                conn.execute(
                    "INSERT INTO messages_fts(rowid, sender_name, channel_name, content) "
                    "SELECT rowid, sender_name, COALESCE(channel_name, ''), content FROM messages"
                )
                logger.info("Rebuilt FTS index for %d existing messages", total)
        except sqlite3.OperationalError as e:
            logger.warning("FTS5 setup skipped (not available): %s", e)
        conn.commit()


def _serialize_message(msg: UnifiedMessage) -> dict:
    return {
        "id": msg.id,
        "platform": msg.platform.value,
        "sender_id": msg.sender_id,
        "sender_name": msg.sender_name,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat(),
        "channel_id": msg.channel_id,
        "channel_name": msg.channel_name,
        "message_type": msg.message_type.value,
        "thread_id": msg.thread_id,
        "reply_to_id": msg.reply_to_id,
        "is_mention": 1 if msg.is_mention else 0,
        "has_attachment": 1 if msg.has_attachment else 0,
        "attachment_type": msg.attachment_type,
        "raw_data": json.dumps(msg.raw_data or {}),
        "ingest_ts": datetime.utcnow().isoformat(),
        "read": 0,
    }


def _deserialize_message(row: sqlite3.Row) -> UnifiedMessage:
    raw = json.loads(row["raw_data"]) if row["raw_data"] else {}
    return UnifiedMessage(
        id=row["id"],
        platform=Platform(row["platform"]),
        sender_id=row["sender_id"],
        sender_name=row["sender_name"],
        content=row["content"],
        timestamp=datetime.fromisoformat(row["timestamp"]),
        channel_id=row["channel_id"],
        channel_name=row["channel_name"],
        message_type=MessageType(row["message_type"]),
        thread_id=row["thread_id"],
        reply_to_id=row["reply_to_id"],
        is_mention=bool(row["is_mention"]),
        has_attachment=bool(row["has_attachment"]),
        attachment_type=row["attachment_type"],
        raw_data=raw,
    )


class MessageStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = path or config.DB_PATH
        _ensure_db(self.path)

    def save_message(self, msg: UnifiedMessage) -> None:
        record = _serialize_message(msg)
        with _connect(self.path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO messages (
                  id, platform, sender_id, sender_name, content, timestamp,
                  channel_id, channel_name, message_type, thread_id, reply_to_id,
                  is_mention, has_attachment, attachment_type, raw_data, ingest_ts, read
                ) VALUES (
                  :id, :platform, :sender_id, :sender_name, :content, :timestamp,
                  :channel_id, :channel_name, :message_type, :thread_id, :reply_to_id,
                  :is_mention, :has_attachment, :attachment_type, :raw_data, :ingest_ts, :read
                )
                """,
                record,
            )
            conn.commit()

    def save_messages(self, messages: Iterable[UnifiedMessage]) -> None:
        records = [_serialize_message(m) for m in messages]
        if not records:
            return
        with _connect(self.path) as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO messages (
                  id, platform, sender_id, sender_name, content, timestamp,
                  channel_id, channel_name, message_type, thread_id, reply_to_id,
                  is_mention, has_attachment, attachment_type, raw_data, ingest_ts, read
                ) VALUES (
                  :id, :platform, :sender_id, :sender_name, :content, :timestamp,
                  :channel_id, :channel_name, :message_type, :thread_id, :reply_to_id,
                  :is_mention, :has_attachment, :attachment_type, :raw_data, :ingest_ts, :read
                )
                """,
                records,
            )
            conn.commit()

    def fetch_messages(
        self,
        platform: Platform,
        since: datetime,
        channel_filter: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[UnifiedMessage]:
        query = """
          SELECT * FROM messages
          WHERE platform = ?
            AND timestamp >= ?
        """
        params = [platform.value, since.isoformat()]
        if channel_filter:
            query += " AND (channel_id LIKE ? OR channel_name LIKE ? OR sender_id LIKE ?)"
            like = f"%{channel_filter}%"
            params.extend([like, like, like])
        query += " ORDER BY timestamp DESC"
        if limit is not None and limit > 0:
            query += " LIMIT ?"
            params.append(int(limit))

        with _connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
        return [_deserialize_message(r) for r in rows]

    def count_messages(self, platform: Platform, since: Optional[datetime] = None) -> int:
        query = "SELECT COUNT(*) FROM messages WHERE platform = ?"
        params = [platform.value]
        if since is not None:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())
        with _connect(self.path) as conn:
            row = conn.execute(query, params).fetchone()
        return int(row[0]) if row else 0

    def search_messages(
        self,
        query: str,
        platform: Optional[str] = None,
        limit: int = 50,
    ) -> List[UnifiedMessage]:
        """Full-text search across messages using FTS5."""
        sql = """
          SELECT m.* FROM messages m
          JOIN messages_fts fts ON m.rowid = fts.rowid
          WHERE messages_fts MATCH ?
        """
        params: list = [query]
        if platform:
            sql += " AND m.platform = ?"
            params.append(platform)
        sql += " ORDER BY m.timestamp DESC LIMIT ?"
        params.append(limit)

        try:
            with _connect(self.path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(sql, params).fetchall()
            return [_deserialize_message(r) for r in rows]
        except sqlite3.OperationalError:
            # FTS5 not available, fall back to LIKE search
            logger.warning("FTS5 not available, falling back to LIKE search")
            return self._like_search(query, platform, limit)

    def _like_search(
        self, query: str, platform: Optional[str], limit: int
    ) -> List[UnifiedMessage]:
        like = f"%{query}%"
        sql = """
          SELECT * FROM messages
          WHERE (content LIKE ? OR sender_name LIKE ? OR channel_name LIKE ?)
        """
        params: list = [like, like, like]
        if platform:
            sql += " AND platform = ?"
            params.append(platform)
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        with _connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
        return [_deserialize_message(r) for r in rows]

    def mark_read(self, platform: str, message_ids: List[str]) -> int:
        """Mark messages as read. Returns number of rows updated."""
        if not message_ids:
            return 0
        placeholders = ",".join("?" for _ in message_ids)
        sql = f"UPDATE messages SET read = 1 WHERE platform = ? AND id IN ({placeholders})"
        params = [platform] + message_ids
        with _connect(self.path) as conn:
            cursor = conn.execute(sql, params)
            conn.commit()
            return cursor.rowcount

    def get_stats(self) -> dict:
        """Return aggregate statistics about stored messages."""
        now = datetime.utcnow()
        day_ago = (now - timedelta(hours=24)).isoformat()
        week_ago = (now - timedelta(days=7)).isoformat()

        with _connect(self.path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            by_platform = {}
            for row in conn.execute(
                "SELECT platform, COUNT(*) as cnt FROM messages GROUP BY platform"
            ):
                by_platform[row[0]] = row[1]
            last_24h = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE timestamp >= ?", [day_ago]
            ).fetchone()[0]
            last_7d = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE timestamp >= ?", [week_ago]
            ).fetchone()[0]
            unread = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE read = 0"
            ).fetchone()[0]

        return {
            "total_messages": total,
            "by_platform": by_platform,
            "last_24h": last_24h,
            "last_7d": last_7d,
            "unread": unread,
        }

    def backup(self, backup_dir: Optional[Path] = None) -> Path:
        """Create a backup of the database. Keeps last MAX_BACKUPS copies."""
        backup_dir = backup_dir or (self.path.parent / "backups")
        backup_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        dest = backup_dir / f"briefing_{ts}.db"

        with _connect(self.path) as src_conn:
            dst_conn = sqlite3.connect(str(dest))
            src_conn.backup(dst_conn)
            dst_conn.close()

        logger.info("Database backed up to %s", dest)

        # Prune old backups
        backups = sorted(backup_dir.glob("briefing_*.db"))
        while len(backups) > MAX_BACKUPS:
            old = backups.pop(0)
            old.unlink()
            logger.info("Deleted old backup: %s", old.name)

        return dest
