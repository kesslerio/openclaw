#!/usr/bin/env python3
"""
Daily Ingest Script

Runs daily automation for Memex:
1. Sync yesterday's emails
2. Sync this week's calendar events
3. Index new data into ChromaDB
4. Generate today's journal (or yesterday's if --journal-only)

Designed to run via cron at 6 AM and 9 PM daily.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from config.model_enforcer import ModelEnforcer, enforce_anthropic_only
from journalist.journal_generator import JournalGenerator
from integrations.gmail_service import GmailService
from integrations.calendar_service import CalendarService
from retrieval.vector_store import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model enforcement
MODEL = enforce_anthropic_only("claude-sonnet-4-20250514")

# Data directories
MEMEX_DIR = Path(__file__).parent.parent
DATA_DIR = MEMEX_DIR / "data"
JOURNALS_DIR = DATA_DIR / "journals"


class DailyIngestor:
    """
    Handles daily data ingestion and journal generation.
    """

    def __init__(self):
        """Initialize services"""
        self.gmail_service = GmailService()
        self.calendar_service = CalendarService()
        self.vector_store = VectorStore()
        self.journal_generator = JournalGenerator()

        # Ensure journals directory exists
        JOURNALS_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("Initialized DailyIngestor")

    def sync_emails(self, days_back: int = 1) -> int:
        """
        Sync emails from the past N days.

        Args:
            days_back: Number of days to sync

        Returns:
            Number of emails synced
        """
        logger.info(f"Syncing emails from last {days_back} day(s)")

        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            # Sync emails
            emails = self.gmail_service.fetch_emails(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )

            logger.info(f"✅ Synced {len(emails)} emails")
            return len(emails)

        except Exception as e:
            logger.error(f"❌ Email sync failed: {e}")
            return 0

    def sync_calendar(self, days_ahead: int = 7) -> int:
        """
        Sync calendar events for the next N days.

        Args:
            days_ahead: Number of days ahead to sync

        Returns:
            Number of events synced
        """
        logger.info(f"Syncing calendar for next {days_ahead} days")

        try:
            # Calculate date range
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)

            # Sync calendar
            events = self.calendar_service.fetch_events(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )

            logger.info(f"✅ Synced {len(events)} calendar events")
            return len(events)

        except Exception as e:
            logger.error(f"❌ Calendar sync failed: {e}")
            return 0

    def index_new_data(self) -> Dict[str, int]:
        """
        Index new emails, events, and transcripts into ChromaDB.

        Returns:
            Dict with counts of indexed items by type
        """
        logger.info("Indexing new data into ChromaDB")

        indexed = {
            'emails': 0,
            'events': 0,
            'transcripts': 0
        }

        try:
            # Index emails
            gmail_dir = DATA_DIR / "integrations" / "gmail"
            if gmail_dir.exists():
                email_files = list(gmail_dir.glob("*.json"))
                # TODO: Implement smart indexing (only new files)
                # For now, this is a placeholder
                indexed['emails'] = len(email_files)

            # Index calendar events
            calendar_dir = DATA_DIR / "integrations" / "calendar"
            if calendar_dir.exists():
                event_files = list(calendar_dir.glob("*.json"))
                indexed['events'] = len(event_files)

            # Index transcripts
            transcripts_dir = DATA_DIR / "transcripts"
            if transcripts_dir.exists():
                transcript_files = list(transcripts_dir.glob("*.json"))
                indexed['transcripts'] = len(transcript_files)

            logger.info(f"✅ Indexed {sum(indexed.values())} items total")
            return indexed

        except Exception as e:
            logger.error(f"❌ Indexing failed: {e}")
            return indexed

    def generate_journal(self, date_str: str = None) -> bool:
        """
        Generate journal for a specific date (default yesterday).

        Args:
            date_str: Date string (YYYY-MM-DD), default yesterday

        Returns:
            True if successful
        """
        # Default to yesterday
        if date_str is None:
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")

        logger.info(f"Generating journal for {date_str}")

        # Check if journal already exists
        journal_path = JOURNALS_DIR / f"{date_str}.md"
        if journal_path.exists():
            logger.info(f"Journal for {date_str} already exists")
            return False

        try:
            # Load data for the date
            from scripts.journal_backfill import JournalBackfiller
            backfiller = JournalBackfiller()

            data = backfiller.load_data_for_date(date_str)
            total_items = len(data['transcripts']) + len(data['emails']) + len(data['events'])

            if total_items == 0:
                logger.info(f"No data for {date_str}")
                return False

            # Format context
            context = backfiller.format_context_for_journal(date_str, data)

            # Generate journal
            journal_data = self.journal_generator.generate_journal(
                date=date_str,
                transcripts=context
            )

            # Add source counts
            journal_data['source_counts'] = {
                'transcripts': len(data['transcripts']),
                'emails': len(data['emails']),
                'events': len(data['events'])
            }

            # Save with frontmatter
            backfiller.save_journal_with_frontmatter(journal_data, journal_path)

            logger.info(f"✅ Generated journal for {date_str}")
            return True

        except Exception as e:
            logger.error(f"❌ Journal generation failed for {date_str}: {e}")
            return False

    def run_full_ingest(self):
        """
        Run full daily ingestion workflow.
        """
        logger.info("🚀 Starting daily ingest")

        # Step 1: Sync emails
        email_count = self.sync_emails(days_back=1)

        # Step 2: Sync calendar
        event_count = self.sync_calendar(days_ahead=7)

        # Step 3: Index new data
        indexed = self.index_new_data()

        # Step 4: Generate yesterday's journal
        journal_generated = self.generate_journal()

        # Summary
        logger.info("✅ Daily ingest complete")
        logger.info(f"  Emails synced: {email_count}")
        logger.info(f"  Events synced: {event_count}")
        logger.info(f"  Items indexed: {sum(indexed.values())}")
        logger.info(f"  Journal generated: {journal_generated}")

    def run_journal_only(self, date_str: str = None):
        """
        Run journal generation only (for 9 PM cron job).

        Args:
            date_str: Date to generate journal for (default yesterday)
        """
        logger.info("📔 Running journal generation only")

        success = self.generate_journal(date_str)

        if success:
            logger.info("✅ Journal generation complete")
        else:
            logger.info("ℹ️  No journal generated")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Daily Memex ingestion and journal generation")
    parser.add_argument("--journal-only", action="store_true",
                        help="Only generate journal, skip sync/indexing")
    parser.add_argument("--date", help="Specific date to process (YYYY-MM-DD)")
    parser.add_argument("--sync-only", action="store_true",
                        help="Only sync data, skip journal generation")

    args = parser.parse_args()

    # Initialize ingestor
    ingestor = DailyIngestor()

    if args.journal_only:
        # Journal-only mode (for 9 PM cron)
        ingestor.run_journal_only(date_str=args.date)

    elif args.sync_only:
        # Sync-only mode
        logger.info("🔄 Syncing data only")
        ingestor.sync_emails()
        ingestor.sync_calendar()
        ingestor.index_new_data()
        logger.info("✅ Sync complete")

    else:
        # Full ingestion (for 6 AM cron)
        ingestor.run_full_ingest()


if __name__ == "__main__":
    main()
