"""
Data models for the Plaud.AI scraper.

This module defines all data structures used by the scraper including:
- Configuration models
- Credentials
- Transcript metadata and content
- Batch export results
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Literal


# ============================================================
# Configuration Models
# ============================================================

@dataclass
class ScraperConfig:
    """Configuration for the Plaud scraper."""

    # Browser settings
    headless: bool = False
    timeout_ms: int = 30000
    viewport_width: int = 1280
    viewport_height: int = 800
    slow_mo: int = 0  # Milliseconds to slow down Playwright operations

    # Rate limiting
    rate_limit_per_second: float = 0.2  # 1 request per 5 seconds

    # Retry settings
    max_retries: int = 3
    retry_backoff_base: float = 2.0  # Exponential backoff multiplier
    retry_initial_delay: float = 1.0  # Initial delay in seconds

    # Session management
    session_timeout_seconds: int = 3600  # 1 hour

    # Output settings
    default_output_format: Literal["json", "txt", "srt"] = "json"
    create_date_subdirs: bool = True
    save_metadata: bool = True


@dataclass
class PlaudCredentials:
    """Authentication credentials for Plaud.AI."""

    email: str
    password: Optional[str] = None  # Optional for OAuth

    # OAuth settings
    use_oauth: bool = False
    oauth_provider: Literal["google", "apple", "email"] = "google"

    # 2FA settings
    two_factor_enabled: bool = False
    two_factor_code: Optional[str] = None


# ============================================================
# Transcript Models
# ============================================================

@dataclass
class TranscriptMetadata:
    """Metadata about a recording/transcript."""

    # Required fields
    id: str
    title: str

    # Optional fields
    date: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    participants: List[str] = field(default_factory=list)
    download_url: Optional[str] = None

    # Additional metadata
    language: str = "en"
    word_count: Optional[int] = None
    speaker_count: Optional[int] = None

    # Processing status
    is_processed: bool = False
    has_transcript: bool = False

    # Source information
    source: str = "plaud"
    external_id: Optional[str] = None  # Original Plaud ID if different

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling datetime serialization."""
        data = asdict(self)
        if self.date:
            data['date'] = self.date.isoformat()
        return data


@dataclass
class TranscriptSegment:
    """A single segment of a transcript (one speaker turn)."""

    speaker_label: str
    text: str
    start_time_ms: int
    end_time_ms: int
    confidence: Optional[float] = None

    # Optional fields
    speaker_name: Optional[str] = None  # Identified name vs label
    timestamp: Optional[str] = None  # Human-readable timestamp

    def duration_ms(self) -> int:
        """Calculate duration of this segment in milliseconds."""
        return self.end_time_ms - self.start_time_ms

    def duration_seconds(self) -> float:
        """Calculate duration of this segment in seconds."""
        return self.duration_ms() / 1000.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TranscriptContent:
    """Full transcript content including metadata and segments."""

    metadata: TranscriptMetadata
    segments: List[TranscriptSegment] = field(default_factory=list)
    raw_text: str = ""
    format: Literal["json", "txt", "srt"] = "json"

    # Additional content
    summary: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metadata": self.metadata.to_dict(),
            "segments": [seg.to_dict() for seg in self.segments],
            "raw_text": self.raw_text,
            "format": self.format,
            "summary": self.summary,
            "keywords": self.keywords,
        }

    def to_plain_text(self) -> str:
        """Convert to readable plain text format."""
        lines = [
            f"# {self.metadata.title}",
            f"Date: {self.metadata.date.strftime('%Y-%m-%d %H:%M:%S') if self.metadata.date else 'Unknown'}",
            f"Duration: {self.metadata.duration_seconds}s" if self.metadata.duration_seconds else "Duration: Unknown",
            f"Speakers: {self.metadata.speaker_count}" if self.metadata.speaker_count else "",
            "",
            "---",
            ""
        ]

        for seg in self.segments:
            speaker = seg.speaker_name or seg.speaker_label
            lines.append(f"**{speaker}** [{seg.timestamp or f'{seg.start_time_ms}ms'}]: {seg.text}")
            lines.append("")

        return "\n".join(lines)

    def to_srt(self) -> str:
        """Convert to SRT subtitle format."""
        lines = []

        for i, seg in enumerate(self.segments, 1):
            start_time = self._ms_to_srt_time(seg.start_time_ms)
            end_time = self._ms_to_srt_time(seg.end_time_ms)

            lines.append(str(i))
            lines.append(f"{start_time} --> {end_time}")
            speaker = seg.speaker_name or seg.speaker_label
            lines.append(f"[{speaker}] {seg.text}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _ms_to_srt_time(ms: int) -> str:
        """Convert milliseconds to SRT time format (HH:MM:SS,mmm)."""
        seconds = ms // 1000
        milliseconds = ms % 1000

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate statistics about the transcript."""
        if not self.segments:
            return {
                "segment_count": 0,
                "word_count": 0,
                "speaker_count": 0,
                "speakers": [],
                "duration_seconds": 0,
            }

        speakers = set(seg.speaker_label for seg in self.segments)
        word_count = sum(len(seg.text.split()) for seg in self.segments)

        # Calculate speaking time per speaker
        speaker_times = {}
        for seg in self.segments:
            speaker = seg.speaker_label
            duration = seg.duration_ms()
            speaker_times[speaker] = speaker_times.get(speaker, 0) + duration

        return {
            "segment_count": len(self.segments),
            "word_count": word_count,
            "speaker_count": len(speakers),
            "speakers": sorted(speakers),
            "speaker_times_ms": speaker_times,
            "duration_seconds": max(seg.end_time_ms for seg in self.segments) / 1000.0 if self.segments else 0,
        }


# ============================================================
# Batch Export Models
# ============================================================

class ExportStatus(Enum):
    """Status of an export operation."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    IN_PROGRESS = "in_progress"


@dataclass
class ExportItem:
    """Result of exporting a single transcript."""

    transcript_id: str
    status: ExportStatus
    output_path: Optional[Path] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None  # Time taken to export

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transcript_id": self.transcript_id,
            "status": self.status.value,
            "output_path": str(self.output_path) if self.output_path else None,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
        }


@dataclass
class BatchExportResult:
    """Result of a batch export operation."""

    # Counts
    success_count: int = 0
    failure_count: int = 0
    skipped_count: int = 0
    total_count: int = 0

    # Details
    items: List[ExportItem] = field(default_factory=list)

    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # Output
    output_dir: Optional[Path] = None
    manifest_path: Optional[Path] = None

    def duration_seconds(self) -> float:
        """Calculate total duration of the export."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.total_count == 0:
            return 0.0
        return (self.success_count / self.total_count) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": {
                "success_count": self.success_count,
                "failure_count": self.failure_count,
                "skipped_count": self.skipped_count,
                "total_count": self.total_count,
                "success_rate": self.success_rate(),
                "duration_seconds": self.duration_seconds(),
            },
            "timing": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
            },
            "output": {
                "output_dir": str(self.output_dir) if self.output_dir else None,
                "manifest_path": str(self.manifest_path) if self.manifest_path else None,
            },
            "items": [item.to_dict() for item in self.items],
        }

    def generate_report(self) -> str:
        """Generate a markdown report of the export."""
        lines = [
            "# Batch Export Report",
            "",
            f"**Date**: {self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else 'Unknown'}",
            f"**Duration**: {self.duration_seconds():.2f}s",
            "",
            "## Summary",
            "",
            f"- Total files: {self.total_count}",
            f"- Successful: {self.success_count}",
            f"- Failed: {self.failure_count}",
            f"- Skipped: {self.skipped_count}",
            f"- Success rate: {self.success_rate():.1f}%",
            "",
        ]

        if self.failure_count > 0:
            lines.append("## Failures")
            lines.append("")
            for item in self.items:
                if item.status == ExportStatus.FAILED:
                    lines.append(f"- `{item.transcript_id}`: {item.error_message}")
            lines.append("")

        if self.output_dir:
            lines.append("## Output")
            lines.append("")
            lines.append(f"Files saved to: `{self.output_dir}`")
            lines.append("")

        return "\n".join(lines)


# ============================================================
# Session Management Models
# ============================================================

@dataclass
class SessionStore:
    """Store for browser session cookies and state."""

    cookies: List[Dict[str, Any]] = field(default_factory=list)
    local_storage: Dict[str, str] = field(default_factory=dict)
    session_storage: Dict[str, str] = field(default_factory=dict)

    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Check if the session is still valid."""
        if not self.expires_at:
            return False
        return datetime.now() < self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cookies": self.cookies,
            "local_storage": self.local_storage,
            "session_storage": self.session_storage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


# ============================================================
# Rate Limiting Models
# ============================================================

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_second: float = 0.2  # 1 request per 5 seconds
    burst_size: int = 1  # Number of requests that can be made in a burst

    def delay_seconds(self) -> float:
        """Calculate delay between requests in seconds."""
        return 1.0 / self.requests_per_second if self.requests_per_second > 0 else 0


# ============================================================
# Error Models
# ============================================================

class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class AuthenticationError(ScraperError):
    """Raised when authentication fails."""
    pass


class NetworkError(ScraperError):
    """Raised when network requests fail."""
    pass


class RateLimitError(ScraperError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class TranscriptNotFoundError(ScraperError):
    """Raised when a transcript cannot be found."""
    pass


class SessionExpiredError(ScraperError):
    """Raised when the session has expired."""
    pass
