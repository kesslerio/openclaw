"""
Context Grid utilities for Memex.
Encodes memory coordinates similar to hippocampal "place" cues.
Signed-off-by: codex_nike
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ContextGrid:
    time_bucket: str
    people: List[str]
    project: Optional[str]
    location: Optional[str]
    medium: Optional[str]
    platform: Optional[str]
    channel: Optional[str]
    thread: Optional[str]
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_bucket": self.time_bucket,
            "people": self.people,
            "project": self.project,
            "location": self.location,
            "medium": self.medium,
            "platform": self.platform,
            "channel": self.channel,
            "thread": self.thread,
            "tags": self.tags,
        }


def build_context_grid(
    *,
    timestamp: datetime,
    people: List[str],
    platform: Optional[str] = None,
    channel: Optional[str] = None,
    thread: Optional[str] = None,
    project: Optional[str] = None,
    location: Optional[str] = None,
    medium: Optional[str] = "text",
    tags: Optional[List[str]] = None,
) -> ContextGrid:
    time_bucket = timestamp.strftime("%Y-%m-%d")
    return ContextGrid(
        time_bucket=time_bucket,
        people=[p for p in people if p],
        project=project or channel,
        location=location,
        medium=medium,
        platform=platform,
        channel=channel,
        thread=thread,
        tags=tags or [],
    )

