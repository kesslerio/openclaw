#!/usr/bin/env python3
"""
Setup script for Gmail and Calendar integrations.

This script helps you authorize both accounts (work and personal)
and test the connections.

Usage:
    python setup_gmail_calendar.py --authorize-all
    python setup_gmail_calendar.py --authorize-gmail arvind@copperdigital.com
    python setup_gmail_calendar.py --authorize-calendar arvind.sarin@gmail.com
    python setup_gmail_calendar.py --test-gmail arvind@copperdigital.com
    python setup_gmail_calendar.py --test-calendar arvind.sarin@gmail.com
"""

import argparse
import logging
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


def authorize_gmail(email: str):
    """Authorize Gmail for an account"""
    logger.info(f"\n🔐 Authorizing Gmail for {email}...")
    logger.info("This will open a browser window for authentication.\n")

    config = GmailConfig(credentials_path=CREDENTIALS_PATH, token_dir=TOKEN_DIR)
    service = GmailService(config=config, account_email=email)

    try:
        service.authorize()
        logger.info(f"✅ Successfully authorized Gmail for {email}")
        logger.info(f"Token saved to: {Path(TOKEN_DIR) / f'gmail_{email}.json'}\n")
        return True

    except Exception as e:
        logger.error(f"❌ Authorization failed: {e}")
        return False


def authorize_calendar(email: str):
    """Authorize Calendar for an account"""
    logger.info(f"\n🔐 Authorizing Calendar for {email}...")
    logger.info("This will open a browser window for authentication.\n")

    config = CalendarConfig(credentials_path=CREDENTIALS_PATH, token_dir=TOKEN_DIR)
    service = CalendarService(config=config, account_email=email)

    try:
        service.authorize()
        logger.info(f"✅ Successfully authorized Calendar for {email}")
        logger.info(f"Token saved to: {Path(TOKEN_DIR) / f'calendar_{email}.json'}\n")
        return True

    except Exception as e:
        logger.error(f"❌ Authorization failed: {e}")
        return False


def test_gmail(email: str):
    """Test Gmail connection"""
    logger.info(f"\n🧪 Testing Gmail connection for {email}...")

    config = GmailConfig(credentials_path=CREDENTIALS_PATH, token_dir=TOKEN_DIR)
    service = GmailService(config=config, account_email=email)

    try:
        service.connect()

        # Fetch last 7 days of emails
        start_date = datetime.now() - timedelta(days=7)
        emails = service.fetch_emails(start_date=start_date, max_emails=10)

        logger.info(f"✅ Connection successful!")
        logger.info(f"   Found {len(emails)} emails from last 7 days")

        if emails:
            logger.info(f"\n📧 Sample (latest 3):")
            for email in emails[:3]:
                logger.info(f"   • {email.date.strftime('%Y-%m-%d')} - {email.subject}")

        return True

    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False


def test_calendar(email: str):
    """Test Calendar connection"""
    logger.info(f"\n🧪 Testing Calendar connection for {email}...")

    config = CalendarConfig(credentials_path=CREDENTIALS_PATH, token_dir=TOKEN_DIR)
    service = CalendarService(config=config, account_email=email)

    try:
        service.connect()

        # List calendars
        calendars = service.list_calendars()
        logger.info(f"✅ Connection successful!")
        logger.info(f"   Found {len(calendars)} calendars")

        # Fetch last 7 days of events
        start_date = datetime.now() - timedelta(days=7)
        events = service.fetch_events(start_date=start_date, max_events=10)

        logger.info(f"   Found {len(events)} events from last 7 days")

        if events:
            logger.info(f"\n📅 Sample (latest 3):")
            for event in events[:3]:
                time_str = event.start.strftime('%Y-%m-%d %H:%M')
                logger.info(f"   • {time_str} - {event.summary}")

        return True

    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Setup Gmail and Calendar integrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Authorize all accounts (work and personal)
  python setup_gmail_calendar.py --authorize-all

  # Authorize specific account
  python setup_gmail_calendar.py --authorize-gmail arvind@copperdigital.com

  # Test connections
  python setup_gmail_calendar.py --test-gmail arvind@copperdigital.com
  python setup_gmail_calendar.py --test-calendar arvind.sarin@gmail.com

  # Test all
  python setup_gmail_calendar.py --test-all
        """,
    )

    parser.add_argument(
        "--authorize-all", action="store_true", help="Authorize all accounts"
    )
    parser.add_argument("--authorize-gmail", help="Authorize Gmail for email address")
    parser.add_argument(
        "--authorize-calendar", help="Authorize Calendar for email address"
    )
    parser.add_argument("--test-gmail", help="Test Gmail connection for email address")
    parser.add_argument(
        "--test-calendar", help="Test Calendar connection for email address"
    )
    parser.add_argument("--test-all", action="store_true", help="Test all connections")

    args = parser.parse_args()

    # Check credentials file
    if not Path(CREDENTIALS_PATH).exists():
        logger.error(f"\n❌ Credentials file not found: {CREDENTIALS_PATH}")
        logger.error("\nPlease download OAuth2 credentials from Google Cloud Console:")
        logger.error("  1. Go to https://console.cloud.google.com")
        logger.error("  2. Create/select project")
        logger.error("  3. Enable Gmail API and Calendar API")
        logger.error("  4. Create OAuth2 credentials (Desktop app)")
        logger.error(f"  5. Download as credentials.json to: {CREDENTIALS_PATH}\n")
        sys.exit(1)

    success = True

    # Authorize all
    if args.authorize_all:
        logger.info("=" * 60)
        logger.info("Authorizing all accounts...")
        logger.info("=" * 60)

        # Gmail
        if not authorize_gmail(WORK_EMAIL):
            success = False
        if not authorize_gmail(PERSONAL_EMAIL):
            success = False

        # Calendar
        if not authorize_calendar(WORK_EMAIL):
            success = False
        if not authorize_calendar(PERSONAL_EMAIL):
            success = False

        if success:
            logger.info("\n✅ All accounts authorized successfully!\n")
        else:
            logger.error("\n❌ Some authorizations failed\n")
            sys.exit(1)

    # Individual authorizations
    if args.authorize_gmail:
        if not authorize_gmail(args.authorize_gmail):
            sys.exit(1)

    if args.authorize_calendar:
        if not authorize_calendar(args.authorize_calendar):
            sys.exit(1)

    # Test all
    if args.test_all:
        logger.info("=" * 60)
        logger.info("Testing all connections...")
        logger.info("=" * 60)

        # Gmail
        if not test_gmail(WORK_EMAIL):
            success = False
        if not test_gmail(PERSONAL_EMAIL):
            success = False

        # Calendar
        if not test_calendar(WORK_EMAIL):
            success = False
        if not test_calendar(PERSONAL_EMAIL):
            success = False

        if success:
            logger.info("\n✅ All tests passed!\n")
        else:
            logger.error("\n❌ Some tests failed\n")
            sys.exit(1)

    # Individual tests
    if args.test_gmail:
        if not test_gmail(args.test_gmail):
            sys.exit(1)

    if args.test_calendar:
        if not test_calendar(args.test_calendar):
            sys.exit(1)

    # No args
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
