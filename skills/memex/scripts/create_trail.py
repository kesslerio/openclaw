#!/usr/bin/env python3
"""
Create or list Memex trails.
Signed-off-by: codex_nike
"""

import argparse
import json
from pathlib import Path

from memex.trails.storage import TrailNode, create_trail, list_trails


def main() -> None:
    parser = argparse.ArgumentParser(description="Memex trail helper")
    parser.add_argument("--name", type=str, help="Trail name")
    parser.add_argument("--description", type=str, default=None)
    parser.add_argument("--tags", type=str, default="")
    parser.add_argument("--nodes-file", type=str, help="Path to JSON list of nodes")
    parser.add_argument("--list", action="store_true", help="List trails")

    args = parser.parse_args()

    if args.list:
        trails = list_trails()
        for t in trails:
            print(f"{t.id} | {t.name} | {len(t.nodes)} nodes | {t.created_at}")
        return

    if not args.name or not args.nodes_file:
        raise SystemExit("--name and --nodes-file are required unless --list is set")

    nodes_path = Path(args.nodes_file)
    nodes_raw = json.loads(nodes_path.read_text(encoding="utf-8"))
    nodes = [TrailNode(**node) for node in nodes_raw]

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    trail = create_trail(
        name=args.name,
        nodes=nodes,
        description=args.description,
        tags=tags,
    )
    print(f"✅ Trail created: {trail.id} ({len(trail.nodes)} nodes)")


if __name__ == "__main__":
    main()
