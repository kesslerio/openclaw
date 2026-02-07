#!/usr/bin/env python3
"""
Smoke tests for Universal Briefing enhancements.
Covers: DB operations, WAL mode, FTS5 search, filter engine, logging, constants, backup.
"""
import hashlib
import os
import re
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set env vars BEFORE importing modules
os.environ.setdefault("WAHA_API_KEY", "test_key_for_tests")
os.environ.setdefault("WAHA_URL", "http://localhost:3000")


class TestConstants(unittest.TestCase):
    """Verify centralized constants are correct."""

    def test_model_id(self):
        from scripts.constants import ANTHROPIC_MODEL
        self.assertEqual(ANTHROPIC_MODEL, "claude-sonnet-4-5-20250929")

    def test_no_old_model_in_processors(self):
        """Ensure claude-3-5-sonnet-20241022 is gone from processor files."""
        processor_dir = Path(__file__).parent.parent / "scripts" / "processors"
        old_model = "claude-3-5-sonnet-20241022"
        for py_file in processor_dir.glob("*.py"):
            content = py_file.read_text()
            self.assertNotIn(
                old_model,
                content,
                f"Old model ID found in {py_file.name}",
            )

    def test_retry_settings(self):
        from scripts.constants import MAX_RETRIES, RETRY_BASE_DELAY, RETRY_MAX_DELAY
        self.assertEqual(MAX_RETRIES, 3)
        self.assertGreater(RETRY_BASE_DELAY, 0)
        self.assertGreater(RETRY_MAX_DELAY, RETRY_BASE_DELAY)


class TestLogging(unittest.TestCase):
    """Verify logging configuration."""

    def test_setup_logging(self):
        from scripts.logging_config import setup_logging, get_logger
        # Reset for test
        import scripts.logging_config as lc
        lc._configured = False
        setup_logging("DEBUG")
        logger = get_logger("test")
        self.assertEqual(logger.name, "ub.test")

    def test_get_logger_namespace(self):
        from scripts.logging_config import get_logger
        logger = get_logger("storage")
        self.assertEqual(logger.name, "ub.storage")


class TestStorage(unittest.TestCase):
    """Verify storage layer enhancements."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = Path(self.tmpdir) / "test.db"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_store(self):
        from scripts.storage import MessageStore
        return MessageStore(path=self.db_path)

    def _make_message(self, msg_id="test1", content="Hello world", platform="whatsapp"):
        from scripts.models import UnifiedMessage, Platform, MessageType
        return UnifiedMessage(
            id=msg_id,
            platform=Platform(platform),
            sender_id="sender1",
            sender_name="Alice",
            content=content,
            timestamp=datetime.utcnow(),
            message_type=MessageType.DIRECT,
        )

    def test_wal_mode(self):
        """Verify WAL journal mode is enabled."""
        store = self._make_store()
        conn = sqlite3.connect(str(self.db_path))
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        self.assertEqual(mode, "wal")

    def test_save_and_fetch(self):
        store = self._make_store()
        msg = self._make_message()
        store.save_message(msg)

        from scripts.models import Platform
        results = store.fetch_messages(
            platform=Platform.WHATSAPP,
            since=datetime.min,
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "Hello world")

    def test_read_column_exists(self):
        """Verify 'read' column was added."""
        store = self._make_store()
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute("PRAGMA table_info(messages)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        self.assertIn("read", columns)

    def test_mark_read(self):
        store = self._make_store()
        msg = self._make_message()
        store.save_message(msg)
        updated = store.mark_read("whatsapp", ["test1"])
        self.assertEqual(updated, 1)

    def test_get_stats(self):
        store = self._make_store()
        msg = self._make_message()
        store.save_message(msg)
        stats = store.get_stats()
        self.assertEqual(stats["total_messages"], 1)
        self.assertIn("whatsapp", stats["by_platform"])
        self.assertIn("last_24h", stats)
        self.assertIn("unread", stats)

    def test_fts_search(self):
        """Verify FTS5 full-text search works."""
        store = self._make_store()
        store.save_message(self._make_message("m1", "The quick brown fox"))
        store.save_message(self._make_message("m2", "A lazy dog sleeps"))

        results = store.search_messages("fox")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "m1")

    def test_fts_search_with_platform(self):
        store = self._make_store()
        store.save_message(self._make_message("m1", "Testing search", "whatsapp"))
        results = store.search_messages("Testing", platform="whatsapp")
        self.assertEqual(len(results), 1)

    def test_backup(self):
        store = self._make_store()
        store.save_message(self._make_message())
        backup_dir = Path(self.tmpdir) / "backups"
        dest = store.backup(backup_dir=backup_dir)
        self.assertTrue(dest.exists())
        # Verify backup has the data
        conn = sqlite3.connect(str(dest))
        count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)


class TestFilterEngine(unittest.TestCase):
    """Verify deterministic content hash."""

    def test_deterministic_hash(self):
        """Hash should be stable across runs (SHA-256, not builtin hash)."""
        from scripts.processors.filter_engine import FilterEngine
        from scripts.models import UnifiedMessage, Platform, MessageType

        engine = FilterEngine(user_identifiers=[])
        msg = UnifiedMessage(
            id="test1",
            platform=Platform.WHATSAPP,
            sender_id="sender1",
            sender_name="Alice",
            content="Hello world",
            timestamp=datetime(2024, 1, 1, 12, 0),
            message_type=MessageType.DIRECT,
        )
        h1 = engine._content_hash(msg)
        h2 = engine._content_hash(msg)
        self.assertEqual(h1, h2)
        # Should be a hex SHA-256 digest (64 chars)
        self.assertEqual(len(h1), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in h1))


class TestApiAuth(unittest.TestCase):
    """Verify auth logic fix in listeners."""

    def test_auth_allows_when_no_token(self):
        """When API_TOKEN is empty, access should be allowed."""
        # We test the logic directly from the source
        from scripts.listeners import run_api_server
        # The fix: _require_auth returns True when no token configured
        # We verify by reading the source
        import inspect
        source = inspect.getsource(run_api_server)
        self.assertIn("return True  # No token configured", source)

    def test_auth_denies_when_wrong_token(self):
        """Source should check token == config.API_TOKEN."""
        from scripts.listeners import run_api_server
        import inspect
        source = inspect.getsource(run_api_server)
        self.assertIn("token == config.API_TOKEN", source)


if __name__ == "__main__":
    unittest.main()
