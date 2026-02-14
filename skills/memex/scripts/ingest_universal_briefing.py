#!/usr/bin/env python3
"""
Ingest Universal Briefing messages into Memex transcripts.
Signed-off-by: codex_nike
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from memex.context_grid import build_context_grid


DEFAULT_DB = Path.home() / ".universal-briefing" / "briefing.db"
DEFAULT_OUT = Path(__file__).resolve().parents[1] / "data" / "transcripts" / "universal-briefing"


@dataclass
class UBMessage:
    id: str
    platform: str
    sender_id: str
    sender_name: str
    content: str
    timestamp: datetime
    channel_id: Optional[str]
    channel_name: Optional[str]
    message_type: str
    thread_id: Optional[str]
    reply_to_id: Optional[str]
    is_mention: bool
    has_attachment: bool


def _safe_slug(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe[:80] or "unknown"


def load_messages(db_path: Path, since: datetime, limit: Optional[int]) -> List[UBMessage]:
    if not db_path.exists():
        raise FileNotFoundError(f"Universal Briefing DB not found: {db_path}")
    query = """
      SELECT
        id, platform, sender_id, sender_name, content, timestamp,
        channel_id, channel_name, message_type, thread_id, reply_to_id,
        is_mention, has_attachment
      FROM messages
      WHERE timestamp >= ?
      ORDER BY timestamp ASC
    """
    params: List[Any] = [since.isoformat()]
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    rows: List[UBMessage] = []
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        for row in conn.execute(query, params).fetchall():
            rows.append(
                UBMessage(
                    id=row["id"],
                    platform=row["platform"],
                    sender_id=row["sender_id"],
                    sender_name=row["sender_name"],
                    content=row["content"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    channel_id=row["channel_id"],
                    channel_name=row["channel_name"],
                    message_type=row["message_type"],
                    thread_id=row["thread_id"],
                    reply_to_id=row["reply_to_id"],
                    is_mention=bool(row["is_mention"]),
                    has_attachment=bool(row["has_attachment"]),
                )
            )
    return rows


def group_messages(messages: List[UBMessage]) -> Dict[Tuple[str, str, str], List[UBMessage]]:
    groups: Dict[Tuple[str, str, str], List[UBMessage]] = defaultdict(list)
    for msg in messages:
        date_key = msg.timestamp.strftime("%Y-%m-%d")
        channel_key = msg.channel_name or msg.channel_id or msg.sender_name or "direct"
        groups[(date_key, msg.platform, channel_key)].append(msg)
    return groups


def write_transcript(
    out_dir: Path,
    date_key: str,
    platform: str,
    channel_key: str,
    messages: List[UBMessage],
) -> Path:
    safe_channel = _safe_slug(channel_key)
    transcript_id = f"ub_{platform}_{date_key}_{safe_channel}"
    out_path = out_dir / date_key
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / f"{transcript_id}.json"

    participants = sorted({m.sender_name for m in messages if m.sender_name})
    title = f"UB {platform} {channel_key} {date_key}"
    raw_lines = []
    segments = []

    for msg in messages:
        line = f"{msg.sender_name}: {msg.content}"
        raw_lines.append(line)
        timestamp_ms = int(msg.timestamp.timestamp() * 1000)
        segments.append(
            {
                "speaker": msg.sender_name,
                "text": msg.content,
                "start_time_ms": timestamp_ms,
                "end_time_ms": timestamp_ms + 1000,
                "timestamp": msg.timestamp.isoformat(),
                "is_mention": msg.is_mention,
                "has_attachment": msg.has_attachment,
            }
        )

    grid = build_context_grid(
        timestamp=messages[0].timestamp,
        people=participants,
        platform=platform,
        channel=channel_key,
        thread=messages[0].thread_id,
        tags=["universal-briefing"],
    )

    payload: Dict[str, Any] = {
        "metadata": {
            "id": transcript_id,
            "title": title,
            "date": date_key,
            "participants": participants,
            "source": "universal-briefing",
            "platform": platform,
            "channel": channel_key,
            "message_type": messages[0].message_type,
            "context_grid": grid.to_dict(),
        },
        "segments": segments,
        "raw_text": "\n".join(raw_lines),
        "format": "json",
        "summary": None,
        "keywords": [],
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return file_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Universal Briefing into Memex")
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB))
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out", type=str, default=str(DEFAULT_OUT))

    args = parser.parse_args()

    since = datetime.utcnow() - timedelta(hours=args.hours)
    limit = args.limit if args.limit > 0 else None
    messages = load_messages(Path(args.db), since, limit)
    groups = group_messages(messages)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for (date_key, platform, channel_key), group in groups.items():
        file_path = write_transcript(out_dir, date_key, platform, channel_key, group)
        total += 1
        print(f"✅ Wrote {file_path}")

    print(f"\nDone. Created {total} transcript files from {len(messages)} messages.")


if __name__ == "__main__":
    main()
