#!/usr/bin/env python3
"""
Database migration script for Memex.

Applies SQL migrations to Supabase PostgreSQL database.

Usage:
    python memex/scripts/migrate_database.py
    python memex/scripts/migrate_database.py --rollback
    python memex/scripts/migrate_database.py --verify
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memex.db import get_db_connection, check_database_health


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_migration_file() -> Path:
    """Get the path to the migration SQL file."""
    base_dir = Path(__file__).parent.parent
    migration_file = base_dir / "schema" / "001_transcripts.sql"

    if not migration_file.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_file}")

    return migration_file


def apply_migration():
    """Apply the database migration."""
    logger.info("Starting database migration...")

    migration_file = get_migration_file()
    logger.info(f"Reading migration from: {migration_file}")

    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    logger.info("Connecting to database...")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                logger.info("Executing migration SQL...")
                cur.execute(migration_sql)

            conn.commit()
            logger.info("Migration committed successfully!")

        # Verify migration
        verify_migration()

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


def verify_migration():
    """Verify that migration was applied correctly."""
    logger.info("Verifying migration...")

    checks = {
        "transcripts table": "SELECT to_regclass('public.transcripts')",
        "transcript_speakers table": "SELECT to_regclass('public.transcript_speakers')",
        "transcript_segments table": "SELECT to_regclass('public.transcript_segments')",
        "search_vector index": "SELECT to_regclass('public.idx_transcripts_search')",
        "embedding index": "SELECT to_regclass('public.idx_segments_embedding')",
        "search_transcripts function": (
            "SELECT COUNT(*) FROM pg_proc WHERE proname = 'search_transcripts'"
        ),
        "v_recent_transcripts view": "SELECT to_regclass('public.v_recent_transcripts')",
    }

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            all_passed = True

            for check_name, check_sql in checks.items():
                cur.execute(check_sql)
                result = cur.fetchone()[0]

                if result:
                    logger.info(f"✓ {check_name}: OK")
                else:
                    logger.error(f"✗ {check_name}: MISSING")
                    all_passed = False

    if all_passed:
        logger.info("All verification checks passed!")
    else:
        logger.error("Some verification checks failed!")
        sys.exit(1)


def rollback_migration():
    """Rollback the migration (drop all tables/functions)."""
    logger.warning("Rolling back migration (this will delete all data)...")

    response = input("Are you sure you want to rollback? Type 'yes' to confirm: ")
    if response.lower() != 'yes':
        logger.info("Rollback cancelled.")
        return

    rollback_sql = """
    -- Drop views
    DROP VIEW IF EXISTS v_recent_transcripts CASCADE;
    DROP VIEW IF EXISTS v_pending_transcripts CASCADE;
    DROP VIEW IF EXISTS v_speaker_stats CASCADE;
    DROP VIEW IF EXISTS v_table_sizes CASCADE;
    DROP VIEW IF EXISTS v_index_usage CASCADE;

    -- Drop functions
    DROP FUNCTION IF EXISTS search_transcripts CASCADE;
    DROP FUNCTION IF EXISTS search_similar_segments CASCADE;
    DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;

    -- Drop tables (cascade will drop foreign keys)
    DROP TABLE IF EXISTS transcript_segments CASCADE;
    DROP TABLE IF EXISTS transcript_speakers CASCADE;
    DROP TABLE IF EXISTS transcripts CASCADE;
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                logger.info("Executing rollback...")
                cur.execute(rollback_sql)

            conn.commit()
            logger.info("Rollback completed successfully!")

    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        raise


def show_status():
    """Show current database status."""
    logger.info("Checking database status...")

    health = check_database_health()

    print("\n" + "=" * 60)
    print("DATABASE STATUS")
    print("=" * 60)

    for key, value in health.items():
        print(f"{key:.<30} {value}")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Table sizes
            cur.execute("""
                SELECT
                    tablename,
                    pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
                FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename LIKE 'transcript%'
                ORDER BY pg_total_relation_size('public.'||tablename) DESC
            """)

            print("\n" + "-" * 60)
            print("TABLE SIZES")
            print("-" * 60)

            for row in cur.fetchall():
                print(f"{row[0]:.<30} {row[1]}")

    print("=" * 60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Memex database migration tool"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback migration (WARNING: deletes all data)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify migration without applying"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current database status"
    )

    args = parser.parse_args()

    # Check environment variables
    if not os.getenv("SUPABASE_URL"):
        logger.error("SUPABASE_URL environment variable not set")
        sys.exit(1)

    if not os.getenv("SUPABASE_DB_PASSWORD"):
        logger.error(
            "SUPABASE_DB_PASSWORD environment variable not set\n"
            "Get it from: Supabase Dashboard > Project Settings > Database"
        )
        sys.exit(1)

    try:
        if args.rollback:
            rollback_migration()
        elif args.verify:
            verify_migration()
        elif args.status:
            show_status()
        else:
            apply_migration()

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
