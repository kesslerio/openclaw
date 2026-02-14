"""
Trail storage for Memex associative paths.
Signed-off-by: codex_nike
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


TRAILS_DIR = Path(__file__).resolve().parents[1] / "data" / "trails"
TRAILS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class TrailNode:
    source: str
    source_id: str
    title: str
    uri: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class Trail:
    id: str
    name: str
    created_at: str
    description: Optional[str]
    tags: List[str]
    nodes: List[TrailNode]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "description": self.description,
            "tags": self.tags,
            "nodes": [asdict(n) for n in self.nodes],
        }


def create_trail(
    name: str,
    nodes: List[TrailNode],
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Trail:
    trail_id = f"trail_{uuid.uuid4().hex[:10]}"
    trail = Trail(
        id=trail_id,
        name=name,
        created_at=datetime.utcnow().isoformat(),
        description=description,
        tags=tags or [],
        nodes=nodes,
    )
    path = TRAILS_DIR / f"{trail_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trail.to_dict(), f, indent=2)
    return trail


def list_trails() -> List[Trail]:
    trails: List[Trail] = []
    for file_path in sorted(TRAILS_DIR.glob("trail_*.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        nodes = [TrailNode(**n) for n in data.get("nodes", [])]
        trails.append(
            Trail(
                id=data.get("id", file_path.stem),
                name=data.get("name", "Untitled"),
                created_at=data.get("created_at", ""),
                description=data.get("description"),
                tags=data.get("tags", []),
                nodes=nodes,
            )
        )
    return trails


def load_trail(trail_id: str) -> Trail:
    path = TRAILS_DIR / f"{trail_id}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = [TrailNode(**n) for n in data.get("nodes", [])]
    return Trail(
        id=data.get("id", trail_id),
        name=data.get("name", "Untitled"),
        created_at=data.get("created_at", ""),
        description=data.get("description"),
        tags=data.get("tags", []),
        nodes=nodes,
    )

