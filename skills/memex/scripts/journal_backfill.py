#!/usr/bin/env python3
"""
Journal Backfill Script

Generates journals for all dates that have existing data (transcripts, emails, calendar events).
Scans data directories from July 2025 to present and creates journal entries.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set
import json
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
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
GMAIL_DIR = DATA_DIR / "integrations" / "gmail"
CALENDAR_DIR = DATA_DIR / "integrations" / "calendar"
JOURNALS_DIR = DATA_DIR / "journals"


class JournalBackfiller:
    """
    Backfills journal entries for dates with existing data.
    """

    def __init__(self, start_date: str = "2025-07-01", end_date: str = None):
        """
        Initialize backfiller.

        Args:
            start_date: Start date (YYYY-MM-DD), default July 1, 2025
            end_date: End date (YYYY-MM-DD), default today
        """
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        self.journal_generator = JournalGenerator()
        self.gmail_service = GmailService()
        self.calendar_service = CalendarService()

        # Ensure journals directory exists
        JOURNALS_DIR.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized JournalBackfiller ({self.start_date.date()} to {self.end_date.date()})")

    def find_dates_with_data(self) -> Set[str]:
        """
        Scan data directories to find all dates with any data.

        Returns:
            Set of date strings (YYYY-MM-DD) that have data
        """
        dates_with_data = set()

        # Scan transcripts directory
        if TRANSCRIPTS_DIR.exists():
            for transcript_file in TRANSCRIPTS_DIR.glob("*.json"):
                try:
                    # Extract date from filename (assumes format: YYYY-MM-DD_*.json)
                    date_str = transcript_file.stem.split('_')[0]
                    # Validate date format
                    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
                        datetime.strptime(date_str, "%Y-%m-%d")  # Validate
                        dates_with_data.add(date_str)
                except Exception as e:
                    logger.debug(f"Could not parse date from {transcript_file.name}: {e}")

        # Scan Gmail directory (structured as account/date/email_*.json)
        if GMAIL_DIR.exists():
            # Look for date directories (YYYY-MM-DD format)
            for account_dir in GMAIL_DIR.iterdir():
                if account_dir.is_dir():
                    for date_dir in account_dir.iterdir():
                        if date_dir.is_dir() and len(date_dir.name) == 10 and date_dir.name[4] == '-':
                            try:
                                # Validate it's a real date
                                datetime.strptime(date_dir.name, "%Y-%m-%d")
                                # Check if there are any email files in this date
                                if list(date_dir.glob("email_*.json")):
                                    dates_with_data.add(date_dir.name)
                            except Exception as e:
                                logger.debug(f"Skipping {date_dir.name}: {e}")

        # Scan Calendar directory (structured as account/date/event_*.json)
        if CALENDAR_DIR.exists():
            for account_dir in CALENDAR_DIR.iterdir():
                if account_dir.is_dir():
                    for date_dir in account_dir.iterdir():
                        if date_dir.is_dir() and len(date_dir.name) == 10 and date_dir.name[4] == '-':
                            try:
                                # Validate it's a real date
                                datetime.strptime(date_dir.name, "%Y-%m-%d")
                                # Check if there are any event files in this date
                                if list(date_dir.glob("event_*.json")):
                                    dates_with_data.add(date_dir.name)
                            except Exception as e:
                                logger.debug(f"Skipping {date_dir.name}: {e}")

        logger.info(f"Found {len(dates_with_data)} dates with data")
        return dates_with_data

    def load_data_for_date(self, date_str: str) -> Dict[str, List]:
        """
        Load all data sources for a specific date.

        Args:
            date_str: Date string (YYYY-MM-DD)

        Returns:
            Dict with 'transcripts', 'emails', 'events' keys
        """
        data = {
            'transcripts': [],
            'emails': [],
            'events': []
        }

        # Load transcripts
        if TRANSCRIPTS_DIR.exists():
            for transcript_file in TRANSCRIPTS_DIR.glob(f"{date_str}_*.json"):
                try:
                    with open(transcript_file) as f:
                        data['transcripts'].append(json.load(f))
                except Exception as e:
                    logger.error(f"Failed to load transcript {transcript_file.name}: {e}")

        # Load emails (nested structure: account/date/email_*.json)
        if GMAIL_DIR.exists():
            for account_dir in GMAIL_DIR.iterdir():
                if account_dir.is_dir():
                    date_dir = account_dir / date_str
                    if date_dir.exists():
                        for email_file in date_dir.glob("email_*.json"):
                            try:
                                with open(email_file) as f:
                                    email_data = json.load(f)
                                    data['emails'].append(email_data)
                            except Exception as e:
                                logger.error(f"Failed to load email {email_file.name}: {e}")

        # Load calendar events (nested structure: account/date/event_*.json)
        if CALENDAR_DIR.exists():
            for account_dir in CALENDAR_DIR.iterdir():
                if account_dir.is_dir():
                    date_dir = account_dir / date_str
                    if date_dir.exists():
                        for event_file in date_dir.glob("event_*.json"):
                            try:
                                with open(event_file) as f:
                                    event_data = json.load(f)
                                    data['events'].append(event_data)
                            except Exception as e:
                                logger.error(f"Failed to load calendar event {event_file.name}: {e}")

        logger.debug(f"{date_str}: {len(data['transcripts'])} transcripts, {len(data['emails'])} emails, {len(data['events'])} events")
        return data

    def format_context_for_journal(self, date_str: str, data: Dict[str, List]) -> List[Dict]:
        """
        Format all data sources into a unified context list for journal generation.

        Args:
            date_str: Date string
            data: Dict with transcripts, emails, events

        Returns:
            List of context dictionaries suitable for JournalGenerator
        """
        context = []

        # Add transcripts
        for transcript in data['transcripts']:
            context.append({
                'type': 'transcript',
                'content': transcript.get('text', ''),
                'timestamp': transcript.get('timestamp', date_str),
                'metadata': transcript.get('metadata', {})
            })

        # Add emails
        for email in data['emails']:
            context.append({
                'type': 'email',
                'content': f"Subject: {email.get('subject', 'No Subject')}\n\n{email.get('snippet', '')}",
                'timestamp': email.get('date', date_str),
                'metadata': {
                    'from': email.get('from', ''),
                    'to': email.get('to', ''),
                }
            })

        # Add calendar events
        for event in data['events']:
            # Handle both dict and string formats
            if isinstance(event, dict):
                start_time = event.get('start', {})
                if isinstance(start_time, dict):
                    timestamp = start_time.get('dateTime', start_time.get('date', date_str))
                else:
                    timestamp = str(start_time) if start_time else date_str

                context.append({
                    'type': 'event',
                    'content': f"{event.get('summary', 'Untitled Event')}: {event.get('description', '')}",
                    'timestamp': timestamp,
                    'metadata': {
                        'location': event.get('location', ''),
                        'attendees': event.get('attendees', [])
                    }
                })
            else:
                logger.warning(f"Unexpected event format: {type(event)}")

        return context

    def generate_journal_for_date(self, date_str: str, skip_existing: bool = True) -> bool:
        """
        Generate journal for a specific date.

        Args:
            date_str: Date string (YYYY-MM-DD)
            skip_existing: Skip if journal already exists

        Returns:
            True if journal was generated, False if skipped
        """
        # Check if journal already exists
        journal_path = JOURNALS_DIR / f"{date_str}.md"
        if skip_existing and journal_path.exists():
            logger.info(f"Journal for {date_str} already exists, skipping")
            return False

        # Load data for this date
        data = self.load_data_for_date(date_str)

        # Check if we have any data
        total_items = len(data['transcripts']) + len(data['emails']) + len(data['events'])
        if total_items == 0:
            logger.info(f"No data for {date_str}, skipping")
            return False

        logger.info(f"Generating journal for {date_str} ({total_items} items)")

        # Format context
        context = self.format_context_for_journal(date_str, data)

        # Generate journal
        try:
            journal_data = self.journal_generator.generate_journal(
                date=date_str,
                transcripts=context  # JournalGenerator accepts generic context
            )

            # Add source counts to metadata
            journal_data['source_counts'] = {
                'transcripts': len(data['transcripts']),
                'emails': len(data['emails']),
                'events': len(data['events'])
            }

            # Save journal with YAML frontmatter
            self.save_journal_with_frontmatter(journal_data, journal_path)

            logger.info(f"✅ Generated journal for {date_str}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to generate journal for {date_str}: {e}")
            return False

    def save_journal_with_frontmatter(self, journal_data: Dict, output_path: Path):
        """
        Save journal with web-ready YAML frontmatter.

        Args:
            journal_data: Journal data from generator
            output_path: Path to save file
        """
        # Build YAML frontmatter
        frontmatter = f"""---
date: {journal_data['date']}
generated_at: {journal_data['generated_at']}
sources:
  transcripts: {journal_data.get('source_counts', {}).get('transcripts', 0)}
  emails: {journal_data.get('source_counts', {}).get('emails', 0)}
  events: {journal_data.get('source_counts', {}).get('events', 0)}
action_items: {len(journal_data.get('action_items', []))}
model: {MODEL}
---

"""
        # Combine frontmatter and journal content
        full_content = frontmatter + journal_data['journal']

        # Write to file
        output_path.write_text(full_content)
        logger.debug(f"Saved journal to {output_path}")

    def run(self, skip_existing: bool = True, max_journals: int = None):
        """
        Run backfill process for all dates with data.

        Args:
            skip_existing: Skip dates that already have journals
            max_journals: Maximum number of journals to generate (for testing)
        """
        logger.info("🚀 Starting journal backfill")

        # Find all dates with data
        dates_with_data = self.find_dates_with_data()

        # Filter to date range
        dates_in_range = [
            d for d in sorted(dates_with_data)
            if self.start_date <= datetime.strptime(d, "%Y-%m-%d") <= self.end_date
        ]

        logger.info(f"Found {len(dates_in_range)} dates in range with data")

        # Generate journals
        generated_count = 0
        skipped_count = 0

        for date_str in dates_in_range:
            if max_journals and generated_count >= max_journals:
                logger.info(f"Reached max journals limit ({max_journals})")
                break

            success = self.generate_journal_for_date(date_str, skip_existing)
            if success:
                generated_count += 1
            else:
                skipped_count += 1

        logger.info(f"✅ Backfill complete: {generated_count} generated, {skipped_count} skipped")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Backfill journal entries for dates with data")
    parser.add_argument("--start-date", default="2025-07-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD), default today")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing journals")
    parser.add_argument("--max", type=int, help="Maximum journals to generate (for testing)")

    args = parser.parse_args()

    # Run backfill
    backfiller = JournalBackfiller(
        start_date=args.start_date,
        end_date=args.end_date
    )

    backfiller.run(
        skip_existing=not args.overwrite,
        max_journals=args.max
    )


if __name__ == "__main__":
    main()
