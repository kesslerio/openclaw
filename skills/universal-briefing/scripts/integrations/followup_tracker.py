"""
Follow-up Tracker
SQLite persistence for commitment tracking
"""
import sqlite3
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

from ..config import config

@dataclass
class TrackedFollowUp:
    id: int
    platform: str
    sender: str
    commitment: str
    deadline: Optional[datetime]
    status: str  # pending, completed, overdue, dismissed
    created_at: datetime
    source_message_id: str

class FollowUpTracker:
    def __init__(self):
        self.db_path = config.DB_PATH
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS followups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                sender TEXT NOT NULL,
                commitment TEXT NOT NULL,
                deadline TIMESTAMP,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_message_id TEXT UNIQUE
            )
        """)
        conn.commit()
        conn.close()

    def add_followup(
        self,
        platform: str,
        sender: str,
        commitment: str,
        deadline: Optional[datetime],
        source_message_id: str
    ) -> Optional[int]:
        """Add a new follow-up"""
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.execute(
                """INSERT OR IGNORE INTO followups
                   (platform, sender, commitment, deadline, source_message_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (platform, sender, commitment, deadline, source_message_id)
            )
            conn.commit()
            return cursor.lastrowid
        except:
            return None
        finally:
            conn.close()

    def get_pending(self) -> List[TrackedFollowUp]:
        """Get all pending follow-ups"""
        conn = sqlite3.connect(str(self.db_path))

        # First update overdue items
        conn.execute("""
            UPDATE followups
            SET status = 'overdue'
            WHERE status = 'pending'
            AND deadline < datetime('now')
        """)
        conn.commit()

        cursor = conn.execute("""
            SELECT * FROM followups
            WHERE status IN ('pending', 'overdue')
            ORDER BY deadline ASC
        """)

        followups = []
        for row in cursor.fetchall():
            followups.append(TrackedFollowUp(
                id=row[0],
                platform=row[1],
                sender=row[2],
                commitment=row[3],
                deadline=datetime.fromisoformat(row[4]) if row[4] else None,
                status=row[5],
                created_at=datetime.fromisoformat(row[6]),
                source_message_id=row[7]
            ))

        conn.close()
        return followups

    def mark_complete(self, followup_id: int):
        """Mark follow-up as completed"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "UPDATE followups SET status = 'completed' WHERE id = ?",
            (followup_id,)
        )
        conn.commit()
        conn.close()
