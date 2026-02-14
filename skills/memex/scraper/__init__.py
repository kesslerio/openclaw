"""
Plaud.AI Scraper Package

This package provides a complete solution for extracting transcripts from Plaud.AI.

Main Components:
- PlaudScraper: Main scraper class with all functionality
- Models: Data structures for configuration and transcript data
- Rate limiting and retry logic
- Session management
- Batch export capabilities

Usage:
    from memex.scraper import PlaudScraper, ScraperConfig, PlaudCredentials

    # Create scraper
    config = ScraperConfig(headless=True, rate_limit_per_second=0.2)
    scraper = PlaudScraper(config)

    # Authenticate
    await scraper.start()
    credentials = PlaudCredentials(email="user@example.com", password="pass")
    await scraper.login(credentials)

    # Export transcripts
    result = await scraper.batch_export(
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 31),
        output_dir=Path("./data/transcripts")
    )

    # Cleanup
    await scraper.close()

For CLI usage:
    python -m memex.scraper.plaud_scraper --email user@example.com --headless
"""

from .models import (
    # Configuration
    ScraperConfig,
    PlaudCredentials,
    RateLimitConfig,

    # Transcript data
    TranscriptMetadata,
    TranscriptContent,
    TranscriptSegment,

    # Export results
    BatchExportResult,
    ExportItem,
    ExportStatus,

    # Session management
    SessionStore,

    # Exceptions
    ScraperError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    TranscriptNotFoundError,
    SessionExpiredError,
)

from .plaud_scraper import (
    PlaudScraper,
    PlaudSelectors,
    RateLimiter,
)


__version__ = "1.0.0"

__all__ = [
    # Main scraper
    "PlaudScraper",
    "PlaudSelectors",
    "RateLimiter",

    # Configuration
    "ScraperConfig",
    "PlaudCredentials",
    "RateLimitConfig",

    # Transcript data
    "TranscriptMetadata",
    "TranscriptContent",
    "TranscriptSegment",

    # Export results
    "BatchExportResult",
    "ExportItem",
    "ExportStatus",

    # Session management
    "SessionStore",

    # Exceptions
    "ScraperError",
    "AuthenticationError",
    "NetworkError",
    "RateLimitError",
    "TranscriptNotFoundError",
    "SessionExpiredError",
]
