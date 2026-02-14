#!/usr/bin/env python3
"""
Sync Gmail and Calendar data for both accounts.

This script fetches emails and calendar events and saves them
to JSON files for the Memex pipeline.

Usage:
    # Sync last 30 days (default)
    python sync_gmail_calendar.py

    # Sync specific date range
    python sync_gmail_calendar.py --start-date 2026-01-01 --end-date 2026-02-04

    # Sync only Gmail
    python sync_gmail_calendar.py --gmail-only

    # Sync only Calendar
    python sync_gmail_calendar.py --calendar-only

    # Sync specific account
    python sync_gmail_calendar.py --email arvind@copperdigital.com
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memex.integrations import GmailService, GmailConfig, CalendarService, CalendarConfig

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Account configuration
WORK_EMAIL = "arvind@copperdigital.com"
PERSONAL_EMAIL = "arvind.sarin@gmail.com"

CREDENTIALS_PATH = str(Path.home() / ".openclaw" / "credentials" / "google_credentials.json")
TOKEN_DIR = str(Path.home() / ".openclaw" / "credentials" / ".tokens")
# Use MEMEX_BASE env var or fallback to repo path
MEMEX_BASE = Path(os.getenv("MEMEX_BASE", Path(__file__).resolve().parents[1]))
DATA_DIR = MEMEX_BASE / "data" / "integrations"


def sync_gmail(email: str, start_date: datetime, end_date: datetime, max_emails: int = 1000):
    """Sync Gmail for an account"""
    logger.info(f"\n📧 Syncing Gmail for {email}...")
    logger.info(f"   Date range: {start_date.date()} to {end_date.date()}")

    config = GmailConfig(credentials_path=CREDENTIALS_PATH, token_dir=TOKEN_DIR)
    service = GmailService(config=config, account_email=email)

    try:
        service.connect()

        output_dir = DATA_DIR / "gmail" / email
        result = service.batch_export(
            output_dir=output_dir,
            start_date=start_date,
            end_date=end_date,
            max_emails=max_emails,
        )

        logger.info(f"✅ Gmail sync complete for {email}")
        logger.info(f"   Fetched: {result.items_fetched} emails")
        logger.info(f"   Saved: {result.items_saved} emails")
        logger.info(f"   Duration: {result.duration_seconds:.1f}s")
        logger.info(f"   Output: {output_dir}")

        if result.errors:
            logger.warning(f"   Errors: {len(result.errors)}")

        return result

    except Exception as e:
        logger.error(f"❌ Gmail sync failed for {email}: {e}")
        raise


def sync_calendar(email: str, start_date: datetime, end_date: datetime, max_events: int = 2500):
    """Sync Calendar for an account"""
    logger.info(f"\n📅 Syncing Calendar for {email}...")
    logger.info(f"   Date range: {start_date.date()} to {end_date.date()}")

    config = CalendarConfig(credentials_path=CREDENTIALS_PATH, token_dir=TOKEN_DIR)
    service = CalendarService(config=config, account_email=email)

    try:
        service.connect()

        output_dir = DATA_DIR / "calendar" / email
        result = service.batch_export(
            output_dir=output_dir,
            calendar_id="primary",
            start_date=start_date,
            end_date=end_date,
            max_events=max_events,
        )

        logger.info(f"✅ Calendar sync complete for {email}")
        logger.info(f"   Fetched: {result.items_fetched} events")
        logger.info(f"   Saved: {result.items_saved} events")
        logger.info(f"   Duration: {result.duration_seconds:.1f}s")
        logger.info(f"   Output: {output_dir}")

        if result.errors:
            logger.warning(f"   Errors: {len(result.errors)}")

        return result

    except Exception as e:
        logger.error(f"❌ Calendar sync failed for {email}: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Sync Gmail and Calendar data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync last 30 days for both accounts
  python sync_gmail_calendar.py

  # Sync specific date range
  python sync_gmail_calendar.py --start-date 2026-01-01 --end-date 2026-02-04

  # Sync only Gmail
  python sync_gmail_calendar.py --gmail-only

  # Sync specific account
  python sync_gmail_calendar.py --email arvind@copperdigital.com

  # Sync with custom limits
  python sync_gmail_calendar.py --max-emails 500 --max-events 1000
        """,
    )

    parser.add_argument(
        "--start-date",
        help="Start date (YYYY-MM-DD). Default: 30 days ago",
        type=str,
    )
    parser.add_argument(
        "--end-date",
        help="End date (YYYY-MM-DD). Default: today",
        type=str,
    )
    parser.add_argument(
        "--email",
        help=f"Specific email to sync (default: both {WORK_EMAIL} and {PERSONAL_EMAIL})",
    )
    parser.add_argument(
        "--gmail-only", action="store_true", help="Sync only Gmail"
    )
    parser.add_argument(
        "--calendar-only", action="store_true", help="Sync only Calendar"
    )
    parser.add_argument(
        "--max-emails",
        type=int,
        default=1000,
        help="Max emails to fetch per account (default: 1000)",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=2500,
        help="Max events to fetch per account (default: 2500)",
    )

    args = parser.parse_args()

    # Parse dates
    if args.start_date:
        start_date = datetime.fromisoformat(args.start_date)
    else:
        start_date = datetime.now() - timedelta(days=30)

    if args.end_date:
        end_date = datetime.fromisoformat(args.end_date)
    else:
        end_date = datetime.now()

    # Determine which accounts to sync
    if args.email:
        emails = [args.email]
    else:
        emails = [WORK_EMAIL, PERSONAL_EMAIL]

    # Determine what to sync
    sync_gmail_enabled = not args.calendar_only
    sync_calendar_enabled = not args.gmail_only

    logger.info("=" * 60)
    logger.info("Memex Gmail & Calendar Sync")
    logger.info("=" * 60)
    logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
    logger.info(f"Accounts: {', '.join(emails)}")
    logger.info(f"Gmail: {'✅' if sync_gmail_enabled else '❌'}")
    logger.info(f"Calendar: {'✅' if sync_calendar_enabled else '❌'}")
    logger.info("=" * 60)

    results = []

    try:
        for email in emails:
            # Gmail sync
            if sync_gmail_enabled:
                result = sync_gmail(email, start_date, end_date, args.max_emails)
                results.append(("Gmail", email, result))

            # Calendar sync
            if sync_calendar_enabled:
                result = sync_calendar(email, start_date, end_date, args.max_events)
                results.append(("Calendar", email, result))

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("✅ SYNC COMPLETE")
        logger.info("=" * 60)

        total_items = sum(r[2].items_saved for r in results)
        total_duration = sum(r[2].duration_seconds for r in results)

        logger.info(f"\n📊 Summary:")
        logger.info(f"   Total items synced: {total_items}")
        logger.info(f"   Total duration: {total_duration:.1f}s")
        logger.info(f"   Output directory: {DATA_DIR}")

        for service_type, email, result in results:
            logger.info(
                f"\n   {service_type} - {email}:"
                f"\n      • Saved: {result.items_saved}"
                f"\n      • Duration: {result.duration_seconds:.1f}s"
                f"\n      • Success rate: {result.success_rate:.1f}%"
            )

        logger.info(f"\n💡 Next steps:")
        logger.info(f"   1. Check data in: {DATA_DIR}")
        logger.info(f"   2. Run Memex ingestion pipeline")
        logger.info(f"   3. Generate daily journals\n")

    except Exception as e:
        logger.error(f"\n❌ Sync failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
