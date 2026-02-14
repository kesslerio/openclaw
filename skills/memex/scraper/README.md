# Plaud.AI Scraper Implementation

Complete implementation of the Plaud.AI web scraper as specified in the ONE-YEAR-ROADMAP-2026.md.

## Overview

This scraper provides a production-ready solution for extracting meeting transcripts from Plaud.AI with:

- **Authentication**: Email/password and OAuth (Google) support with 2FA
- **Session Management**: Cookie-based persistence with automatic expiry
- **Rate Limiting**: Token bucket implementation (1 request per 5 seconds)
- **Retry Logic**: Exponential backoff for network failures
- **Batch Export**: Incremental downloads with manifest tracking
- **Multiple Formats**: JSON, TXT, and SRT output
- **Progress Tracking**: Real-time callbacks for batch operations

## Architecture

```
memex/scraper/
├── __init__.py           # Package exports
├── models.py             # Data models and exceptions
├── plaud_scraper.py      # Main scraper implementation
└── README.md             # This file
```

## Installation

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Install from package
cd /Users/arvindsarin/Cursor/Claude-2026/clawd/memex
pip install -e .
```

## Usage

### Basic Usage (Python API)

```python
import asyncio
from datetime import datetime
from pathlib import Path
from memex.scraper import PlaudScraper, ScraperConfig, PlaudCredentials

async def main():
    # Create configuration
    config = ScraperConfig(
        headless=True,
        rate_limit_per_second=0.2,  # 1 request per 5 seconds
        max_retries=3
    )

    # Create scraper
    scraper = PlaudScraper(config)

    try:
        # Start browser
        await scraper.start()

        # Login
        credentials = PlaudCredentials(
            email="user@example.com",
            password="your-password"
        )
        await scraper.login(credentials)

        # Save session for reuse
        await scraper.save_session(Path("session.json"))

        # Fetch transcript list
        transcripts = await scraper.fetch_transcript_list(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 31),
            limit=100
        )
        print(f"Found {len(transcripts)} transcripts")

        # Download single transcript
        content = await scraper.download_transcript(
            transcript_id=transcripts[0].id,
            output_format="json"
        )
        print(f"Downloaded: {content.metadata.title}")

        # Batch export all transcripts
        def on_progress(current, total, transcript_id):
            print(f"Progress: {current}/{total} - {transcript_id}")

        result = await scraper.batch_export(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 31),
            output_dir=Path("./data/transcripts"),
            progress_callback=on_progress,
            formats=["json", "txt", "srt"]
        )

        print(f"Export complete: {result.success_count} succeeded, "
              f"{result.failure_count} failed")

    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Session Reuse

```python
# First run: login and save session
await scraper.login(credentials)
await scraper.save_session(Path("session.json"))

# Later runs: restore session (no login needed)
scraper = PlaudScraper(config)
await scraper.start()
if await scraper.restore_session(Path("session.json")):
    # Session valid, can start scraping
    pass
else:
    # Session expired, need to login again
    await scraper.login(credentials)
```

### CLI Usage

```bash
# Export all transcripts
python -m memex.scraper.plaud_scraper \
    --email user@example.com \
    --password your-password \
    --output ./data/transcripts

# Export with saved session
python -m memex.scraper.plaud_scraper \
    --session session.json \
    --output ./data/transcripts

# Export date range
python -m memex.scraper.plaud_scraper \
    --email user@example.com \
    --start-date 2026-01-01 \
    --end-date 2026-01-31 \
    --output ./data/transcripts

# Export in headless mode
python -m memex.scraper.plaud_scraper \
    --email user@example.com \
    --headless \
    --formats json,txt,srt
```

## Data Models

### ScraperConfig

Configuration for the scraper:

```python
config = ScraperConfig(
    # Browser settings
    headless=False,
    timeout_ms=30000,
    viewport_width=1280,
    viewport_height=800,
    slow_mo=0,

    # Rate limiting
    rate_limit_per_second=0.2,  # 1 request per 5 seconds

    # Retry settings
    max_retries=3,
    retry_backoff_base=2.0,
    retry_initial_delay=1.0,

    # Session management
    session_timeout_seconds=3600,

    # Output settings
    default_output_format="json",
    create_date_subdirs=True,
    save_metadata=True
)
```

### PlaudCredentials

Authentication credentials:

```python
# Email/password
credentials = PlaudCredentials(
    email="user@example.com",
    password="your-password"
)

# OAuth (Google)
credentials = PlaudCredentials(
    email="user@example.com",
    use_oauth=True,
    oauth_provider="google"
)

# With 2FA
credentials = PlaudCredentials(
    email="user@example.com",
    password="your-password",
    two_factor_enabled=True
)
```

### TranscriptMetadata

Metadata about a transcript:

```python
@dataclass
class TranscriptMetadata:
    id: str
    title: str
    date: Optional[datetime]
    duration_seconds: Optional[int]
    participants: List[str]
    download_url: Optional[str]
    language: str = "en"
    word_count: Optional[int]
    speaker_count: Optional[int]
    is_processed: bool = False
    has_transcript: bool = False
    source: str = "plaud"
```

### TranscriptContent

Full transcript with segments:

```python
@dataclass
class TranscriptContent:
    metadata: TranscriptMetadata
    segments: List[TranscriptSegment]
    raw_text: str
    format: Literal["json", "txt", "srt"]
    summary: Optional[str]
    keywords: List[str]

    def to_plain_text(self) -> str: ...
    def to_srt(self) -> str: ...
    def calculate_statistics(self) -> Dict[str, Any]: ...
```

### TranscriptSegment

Individual speaker segment:

```python
@dataclass
class TranscriptSegment:
    speaker_label: str
    text: str
    start_time_ms: int
    end_time_ms: int
    confidence: Optional[float]
    speaker_name: Optional[str]
    timestamp: Optional[str]

    def duration_ms(self) -> int: ...
    def duration_seconds(self) -> float: ...
```

### BatchExportResult

Result of batch export operation:

```python
@dataclass
class BatchExportResult:
    success_count: int
    failure_count: int
    skipped_count: int
    total_count: int
    items: List[ExportItem]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    output_dir: Optional[Path]
    manifest_path: Optional[Path]

    def duration_seconds(self) -> float: ...
    def success_rate(self) -> float: ...
    def generate_report(self) -> str: ...
```

## Output Structure

The batch export creates the following structure:

```
output_dir/
├── manifest.json           # Tracking exported/failed transcripts
├── export-report.md        # Summary report
├── 2026-02-01/            # Date-based subdirectories
│   ├── meeting-001.json   # Structured JSON
│   ├── meeting-001.txt    # Plain text
│   ├── meeting-001.srt    # SRT subtitles
│   └── metadata.json      # Metadata for all files in this date
└── 2026-02-02/
    └── ...
```

### manifest.json

```json
{
  "exported": ["meeting-001", "meeting-002"],
  "failed": [
    {
      "id": "meeting-003",
      "error": "Transcript not found",
      "timestamp": "2026-02-03T10:30:00"
    }
  ]
}
```

### JSON Format

```json
{
  "metadata": {
    "id": "meeting-001",
    "title": "Team Standup",
    "date": "2026-02-01T10:00:00",
    "duration_seconds": 1800,
    "speaker_count": 3,
    "word_count": 2500
  },
  "segments": [
    {
      "speaker_label": "Speaker 1",
      "text": "Good morning everyone...",
      "start_time_ms": 0,
      "end_time_ms": 5000,
      "confidence": 0.95
    }
  ],
  "raw_text": "Speaker 1: Good morning everyone...",
  "format": "json"
}
```

### TXT Format

```
# Team Standup
Date: 2026-02-01 10:00:00
Duration: 1800s
Speakers: 3

---

**Speaker 1** [0ms]: Good morning everyone...

**Speaker 2** [5000ms]: Thanks for joining...
```

### SRT Format

```
1
00:00:00,000 --> 00:00:05,000
[Speaker 1] Good morning everyone...

2
00:00:05,000 --> 00:00:10,000
[Speaker 2] Thanks for joining...
```

## Error Handling

The scraper provides comprehensive error handling:

```python
from memex.scraper import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    TranscriptNotFoundError,
    SessionExpiredError
)

try:
    await scraper.login(credentials)
except AuthenticationError as e:
    print(f"Login failed: {e}")

try:
    content = await scraper.download_transcript("id-123")
except TranscriptNotFoundError:
    print("Transcript doesn't exist")
except NetworkError as e:
    print(f"Network error after retries: {e}")
```

## Rate Limiting

The scraper implements a token bucket rate limiter:

- Default: 1 request per 5 seconds (0.2 requests/second)
- Configurable burst size (default: 1)
- Automatic waiting between requests
- Respects rate limits across all operations

```python
config = ScraperConfig(
    rate_limit_per_second=0.2  # 1 request per 5 seconds
)
```

## Retry Logic

Automatic retry with exponential backoff:

- Default: 3 retries
- Base backoff multiplier: 2.0
- Initial delay: 1.0 seconds
- Delays: 1s, 2s, 4s

```python
config = ScraperConfig(
    max_retries=3,
    retry_backoff_base=2.0,
    retry_initial_delay=1.0
)
```

## Session Management

Sessions are persisted with:

- Browser cookies
- Creation timestamp
- Expiry timestamp (default: 1 hour)
- Automatic validation on restore

```python
# Save session
await scraper.save_session(Path("session.json"))

# Restore session (returns False if expired)
if await scraper.restore_session(Path("session.json")):
    print("Session restored")
else:
    print("Session expired, login required")
```

## Testing

The implementation follows the test specifications in the roadmap. Key test categories:

1. **Authentication Tests**
   - Login success
   - Invalid credentials
   - 2FA handling
   - Session persistence

2. **Transcript List Tests**
   - Basic fetching
   - Pagination
   - Empty date ranges

3. **Download Tests**
   - JSON format
   - TXT format
   - Retry on failure

4. **Batch Export Tests**
   - Basic export
   - Incremental (skip downloaded)
   - Progress callbacks

5. **Rate Limiting Tests**
   - Verify timing between requests

6. **Error Handling Tests**
   - Session expiry
   - Rate limit responses

## Performance

Expected performance characteristics:

- **Rate**: 1 transcript per 5 seconds (720 per hour)
- **Batch Export**: 100 transcripts in ~8-10 minutes
- **Memory**: Low footprint (streaming downloads)
- **Retry Overhead**: 3-7 seconds per failed download

## Logging

The scraper uses Python's logging module:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable debug logging
logging.getLogger('memex.scraper').setLevel(logging.DEBUG)
```

## Roadmap Compliance

This implementation fully complies with the specifications in:

- `/Users/arvindsarin/Cursor/Claude-2026/clawd/plans/ONE-YEAR-ROADMAP-2026.md` (lines 52-510)

Key features implemented:

- ✅ PlaudScraper class with all methods
- ✅ ScraperConfig data model
- ✅ PlaudCredentials with OAuth support
- ✅ TranscriptMetadata with all fields
- ✅ TranscriptContent with segments
- ✅ BatchExportResult with statistics
- ✅ Rate limiting (1 req/5s)
- ✅ Retry logic with exponential backoff
- ✅ Session persistence
- ✅ 2FA support
- ✅ Progress callbacks
- ✅ Incremental downloads (manifest)
- ✅ Multiple output formats (JSON, TXT, SRT)
- ✅ Date-based subdirectories
- ✅ Export reports
- ✅ Comprehensive error handling
- ✅ Type hints throughout
- ✅ Async/await patterns

## Next Steps

To integrate with the Memex pipeline:

1. **Database Ingestion**: Import transcripts into PostgreSQL using the schema in the roadmap
2. **Embedding Generation**: Generate vector embeddings for segments
3. **Journal Generation**: Use HISTORIAN to create daily journals
4. **API Integration**: Expose transcripts via FastAPI endpoints

## License

Part of the Clawd Memex system.

## Author

Nike (Claude)
Created: February 1, 2026
Updated: February 3, 2026
