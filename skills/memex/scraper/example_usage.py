#!/usr/bin/env python3
"""
Example usage of the Plaud.AI scraper.

This script demonstrates:
1. Basic authentication
2. Fetching transcript list
3. Downloading individual transcripts
4. Batch export with progress tracking
5. Session reuse

Usage:
    python example_usage.py --email user@example.com --password your-password
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import argparse

from memex.scraper import (
    PlaudScraper,
    ScraperConfig,
    PlaudCredentials,
    AuthenticationError,
    NetworkError,
)


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_basic_usage(email: str, password: str):
    """Example: Basic usage with login and single transcript download."""

    logger.info("=== Example 1: Basic Usage ===")

    # Create configuration
    config = ScraperConfig(
        headless=True,  # Run in background
        rate_limit_per_second=0.2,  # 1 request per 5 seconds
        max_retries=3
    )

    # Create scraper
    scraper = PlaudScraper(config)

    try:
        # Start browser
        await scraper.start()
        logger.info("Browser started")

        # Login
        credentials = PlaudCredentials(email=email, password=password)

        try:
            await scraper.login(credentials)
            logger.info("Login successful")
        except AuthenticationError as e:
            logger.error(f"Login failed: {e}")
            return

        # Save session for later reuse
        session_path = Path("plaud_session.json")
        await scraper.save_session(session_path)
        logger.info(f"Session saved to {session_path}")

        # Fetch transcript list (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        transcripts = await scraper.fetch_transcript_list(
            start_date=start_date,
            end_date=end_date,
            limit=10
        )

        logger.info(f"Found {len(transcripts)} transcripts")

        # Display transcript info
        for i, t in enumerate(transcripts, 1):
            logger.info(f"  {i}. {t.title} ({t.date}) - {t.duration_seconds}s")

        # Download first transcript if available
        if transcripts:
            first = transcripts[0]
            logger.info(f"Downloading: {first.title}")

            try:
                content = await scraper.download_transcript(
                    transcript_id=first.id,
                    output_format="json"
                )

                logger.info(f"Downloaded successfully:")
                logger.info(f"  Title: {content.metadata.title}")
                logger.info(f"  Segments: {len(content.segments)}")
                logger.info(f"  Words: {content.metadata.word_count}")
                logger.info(f"  Speakers: {content.metadata.speaker_count}")

                # Show first few segments
                logger.info("  First 3 segments:")
                for seg in content.segments[:3]:
                    logger.info(f"    {seg.speaker_label}: {seg.text[:50]}...")

            except NetworkError as e:
                logger.error(f"Download failed: {e}")

    finally:
        await scraper.close()
        logger.info("Browser closed")


async def example_session_reuse():
    """Example: Reuse saved session without logging in again."""

    logger.info("=== Example 2: Session Reuse ===")

    config = ScraperConfig(headless=True)
    scraper = PlaudScraper(config)

    try:
        await scraper.start()

        # Try to restore session
        session_path = Path("plaud_session.json")

        if not session_path.exists():
            logger.error("No saved session found. Run example 1 first.")
            return

        if await scraper.restore_session(session_path):
            logger.info("Session restored successfully")

            # Can now use scraper without logging in
            transcripts = await scraper.fetch_transcript_list(limit=5)
            logger.info(f"Fetched {len(transcripts)} transcripts using saved session")

        else:
            logger.warning("Session expired or invalid. Need to login again.")

    finally:
        await scraper.close()


async def example_batch_export(email: str, password: str):
    """Example: Batch export all transcripts from last month."""

    logger.info("=== Example 3: Batch Export ===")

    config = ScraperConfig(
        headless=True,
        rate_limit_per_second=0.2,
        create_date_subdirs=True
    )

    scraper = PlaudScraper(config)

    try:
        await scraper.start()

        # Authenticate (or restore session)
        session_path = Path("plaud_session.json")

        if session_path.exists() and await scraper.restore_session(session_path):
            logger.info("Using saved session")
        else:
            credentials = PlaudCredentials(email=email, password=password)
            await scraper.login(credentials)
            await scraper.save_session(session_path)

        # Define date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        output_dir = Path("./data/transcripts")

        # Progress callback
        def on_progress(current: int, total: int, transcript_id: str):
            percent = (current / total) * 100
            logger.info(f"Progress: {current}/{total} ({percent:.1f}%) - {transcript_id}")

        # Batch export
        logger.info(f"Exporting transcripts from {start_date.date()} to {end_date.date()}")

        result = await scraper.batch_export(
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir,
            progress_callback=on_progress,
            formats=["json", "txt"]
        )

        # Display results
        logger.info("\n" + "="*60)
        logger.info("EXPORT SUMMARY")
        logger.info("="*60)
        logger.info(f"Total: {result.total_count}")
        logger.info(f"Success: {result.success_count}")
        logger.info(f"Failed: {result.failure_count}")
        logger.info(f"Skipped: {result.skipped_count}")
        logger.info(f"Success rate: {result.success_rate():.1f}%")
        logger.info(f"Duration: {result.duration_seconds():.1f}s")
        logger.info(f"Output: {result.output_dir}")
        logger.info("="*60)

        # Show report
        report_path = output_dir / "export-report.md"
        if report_path.exists():
            logger.info(f"\nReport saved to: {report_path}")

    finally:
        await scraper.close()


async def example_incremental_export():
    """Example: Incremental export (only downloads new transcripts)."""

    logger.info("=== Example 4: Incremental Export ===")

    config = ScraperConfig(headless=True)
    scraper = PlaudScraper(config)

    try:
        await scraper.start()

        # Restore session
        session_path = Path("plaud_session.json")
        if not await scraper.restore_session(session_path):
            logger.error("No valid session. Run example 3 first.")
            return

        # Run batch export again
        # This will skip transcripts already in manifest.json
        output_dir = Path("./data/transcripts")

        result = await scraper.batch_export(
            output_dir=output_dir,
            formats=["json", "txt"]
        )

        logger.info(f"\nIncremental export complete:")
        logger.info(f"  New downloads: {result.success_count}")
        logger.info(f"  Skipped (already downloaded): {result.skipped_count}")
        logger.info(f"  Failed: {result.failure_count}")

    finally:
        await scraper.close()


async def example_with_2fa(email: str, password: str):
    """Example: Login with 2FA enabled."""

    logger.info("=== Example 5: 2FA Login ===")

    config = ScraperConfig(headless=False)  # Need to see browser for 2FA
    scraper = PlaudScraper(config)

    try:
        await scraper.start()

        # 2FA callback
        async def get_2fa_code():
            # In production, this could:
            # - Read from SMS/email
            # - Prompt user via CLI
            # - Use TOTP generator
            code = input("Enter 2FA code: ")
            return code

        credentials = PlaudCredentials(
            email=email,
            password=password,
            two_factor_enabled=True
        )

        await scraper.login(credentials, two_factor_callback=get_2fa_code)
        logger.info("Login with 2FA successful")

        # Save session
        await scraper.save_session(Path("plaud_session_2fa.json"))

    finally:
        await scraper.close()


async def main():
    parser = argparse.ArgumentParser(description='Plaud.AI Scraper Examples')
    parser.add_argument('--email', help='Email for login')
    parser.add_argument('--password', help='Password')
    parser.add_argument('--example', type=int, default=1,
                       help='Example number to run (1-5)')

    args = parser.parse_args()

    if args.example == 1:
        if not args.email or not args.password:
            parser.error("--email and --password required for example 1")
        await example_basic_usage(args.email, args.password)

    elif args.example == 2:
        await example_session_reuse()

    elif args.example == 3:
        if not args.email or not args.password:
            parser.error("--email and --password required for example 3")
        await example_batch_export(args.email, args.password)

    elif args.example == 4:
        await example_incremental_export()

    elif args.example == 5:
        if not args.email or not args.password:
            parser.error("--email and --password required for example 5")
        await example_with_2fa(args.email, args.password)

    else:
        parser.error(f"Invalid example number: {args.example}")


if __name__ == "__main__":
    asyncio.run(main())
