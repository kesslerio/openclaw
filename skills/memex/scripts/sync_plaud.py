#!/usr/bin/env python3
"""
Sync Plaud Transcripts → Local Export → FAISS Index

Chains PlaudExporter (download new transcripts from Plaud API)
with TranscriptIndexer (embed + index into FAISS).

Usage:
    # Incremental sync (default) - only new transcripts
    python3 -m memex.scripts.sync_plaud

    # With rate limit control
    python3 -m memex.scripts.sync_plaud --rate-limit 0.5

    # Retry previously failed exports
    python3 -m memex.scripts.sync_plaud --include-failed

Designed to run via cron:
    0 6,21 * * * cd ~/Cursor/Claude-2026/openclaw/skills/memex && python3 -m memex.scripts.sync_plaud >> /tmp/memex_sync.log 2>&1
"""

import logging
import sys
import time
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memex.scraper.plaud_api_client import PlaudExporter, PlaudClient
from memex.historian.transcript_indexer import TranscriptIndexer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def sync_plaud(
    rate_limit: float = 1.0,
    include_failed: bool = False,
    export_limit: int = 0,
) -> Dict:
    """
    Full sync pipeline: export from Plaud API → index into FAISS.

    Returns:
        Dict with export_stats and index_stats.
    """
    result = {
        "export": {"total": 0, "exported": 0, "skipped": 0, "failed": 0, "no_transcript": 0},
        "index": {"new": 0, "skipped": 0, "errors": 0, "chunks": 0},
        "error": None,
    }

    # Step 1: Export new transcripts from Plaud API
    logger.info("Step 1/2: Exporting new transcripts from Plaud API...")
    try:
        exporter = PlaudExporter()
        if include_failed:
            exporter.manifest["failed"] = {}
        export_stats = exporter.export_all(
            limit=export_limit,
            skip_existing=True,
            rate_limit=rate_limit,
        )
        result["export"] = export_stats
        logger.info(
            f"Export done: {export_stats['exported']} new, "
            f"{export_stats['skipped']} skipped, "
            f"{export_stats['failed']} failed"
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        result["error"] = f"Export failed: {e}"
        return result

    # Step 2: Index new transcripts into FAISS
    logger.info("Step 2/2: Indexing new transcripts into FAISS...")
    try:
        indexer = TranscriptIndexer()
        index_stats = indexer.index_directory()
        result["index"] = index_stats
        logger.info(
            f"Index done: {index_stats['new']} new, "
            f"{index_stats['skipped']} skipped, "
            f"{index_stats['chunks']} chunks"
        )
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        result["error"] = f"Indexing failed: {e}"

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sync Plaud transcripts and index into FAISS")
    parser.add_argument("--rate-limit", type=float, default=1.0, help="Seconds between Plaud API calls")
    parser.add_argument("--include-failed", action="store_true", help="Retry previously failed exports")
    parser.add_argument("--limit", type=int, default=0, help="Max files to export (0=all)")
    args = parser.parse_args()

    start = time.time()
    result = sync_plaud(
        rate_limit=args.rate_limit,
        include_failed=args.include_failed,
        export_limit=args.limit,
    )
    elapsed = time.time() - start

    print(f"\nSync complete in {elapsed:.1f}s:")
    print(f"  Export: {result['export']['exported']} new transcripts downloaded")
    print(f"  Index:  {result['index']['new']} new transcripts indexed ({result['index']['chunks']} chunks)")
    if result["error"]:
        print(f"  Error:  {result['error']}")


if __name__ == "__main__":
    main()
