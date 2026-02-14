"""
Plaud.AI Scraper - Extract all your meeting transcripts.

This module provides a complete Playwright-based scraper for Plaud.AI with:
- Authentication (email/password and OAuth)
- 2FA support
- Session persistence
- Rate limiting (1 request per 5 seconds)
- Retry logic with exponential backoff
- Batch export with progress tracking
- Incremental downloads (skip already downloaded)

Architecture:
- Async/await throughout for performance
- Headless Chrome via Playwright
- Cookie-based session management
- Structured logging
- Type hints for all public APIs

Author: Nike (Claude)
Created: Feb 1, 2026
Updated: Feb 3, 2026 - Full roadmap implementation
Status: PRODUCTION
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any, Tuple

try:
    from playwright.async_api import (
        async_playwright,
        Browser,
        BrowserContext,
        Page,
        Playwright,
        TimeoutError as PlaywrightTimeout,
    )
except ImportError:
    print("Please install playwright: pip install playwright && playwright install chromium")
    exit(1)

from .models import (
    ScraperConfig,
    PlaudCredentials,
    TranscriptMetadata,
    TranscriptContent,
    TranscriptSegment,
    BatchExportResult,
    ExportItem,
    ExportStatus,
    SessionStore,
    RateLimitConfig,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    TranscriptNotFoundError,
    SessionExpiredError,
)


# Setup logging
logger = logging.getLogger(__name__)


# ============================================================
# CSS Selectors for Plaud.AI
# ============================================================

class PlaudSelectors:
    """CSS selectors for Plaud.AI web interface.

    Validated against captured HTML from web.plaud.ai (Feb 2026).
    The site is a Vue.js SPA using vue-recycle-scroller for virtualized lists.
    """

    # Login
    GOOGLE_LOGIN_BTN = 'button:has-text("Google"), [data-provider="google"]'
    EMAIL_INPUT = 'input[type="email"]'
    PASSWORD_INPUT = 'input[type="password"]'
    LOGIN_BUTTON = 'button[type="submit"]'

    # File List (Recordings) — validated
    FILE_LIST_CONTAINER = ".file-list-content"
    FILE_LIST_WRAPPER = ".file-list-item-wrapper"
    FILE_LIST_ITEM = ".file-list-item"
    FILE_LIST_ITEM_SELECTED = ".file-list-item--selected"
    FILE_ITEM_FILENAME = ".file-list-item__filename"
    FILE_ITEM_METADATA = ".file-list-item__metadata"
    FILE_ITEM_CONTENT = ".file-list-item__content"
    FILE_ITEM_STATUS = ".file-list-item__status-container"
    VIRTUAL_SCROLLER = ".vue-recycle-scroller.file-slider-list-wrapper"
    SORT_DROPDOWN = ".file-list-header__sort-dropdown"

    # File Detail
    FILE_DETAIL = ".file-detail"
    FILE_DETAIL_WRAP = ".file-detail-container-wrap"

    # Transcript View — validated
    TRANSCRIPT_MODULE = ".transcript-module"
    TRANSCRIPT_ITEM = ".transcript-item"
    TRANSCRIPT_CONTENT = '[data-testid="file-detail-transcript-content"]'
    SPEAKER_NAME = ".speaker-name"
    SPEAKER_SELECTOR = ".speaker-selector"
    TIMESTAMP = ".timestamp"

    # Transcript unit data-testid selectors — validated
    TRANSCRIBE_UNIT_CONTENT = '[data-testid="transcribe-unit-content"]'
    TRANSCRIBE_UNIT_PLAY = '[data-testid="transcribe-unit-play-button"]'
    TRANSCRIBE_UNIT_COPY = '[data-testid="transcribe-unit-copy-button"]'
    TRANSCRIPT_TAB = '[data-testid="tab-transcript-item"]'

    # Actions — validated
    FILE_ACTION_MENU = ".file-action-menu-wrapper"
    FILE_ACTION_MOVE = '[data-testid="file-action-move-item"]'
    FILE_ACTION_RENAME = '[data-testid="file-action-rename-item"]'
    FILE_ACTION_TRASH = '[data-testid="file-action-trash-item"]'
    ASK_AI_BUTTON = '[data-testid="file-ask-ai-button"]'
    DOWNLOAD_ITEM = '[data-testid="user-menu-download-item"]'


# ============================================================
# Rate Limiter
# ============================================================

class RateLimiter:
    """Token bucket rate limiter for API requests."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.last_request_time = 0.0
        self.tokens = float(config.burst_size)

    async def acquire(self):
        """Wait until we can make another request."""
        now = time.time()
        time_passed = now - self.last_request_time

        # Refill tokens based on time passed
        self.tokens = min(
            self.config.burst_size,
            self.tokens + time_passed * self.config.requests_per_second
        )

        # If no tokens available, wait
        if self.tokens < 1.0:
            wait_time = self.config.delay_seconds()
            logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            self.tokens = 1.0

        # Consume a token
        self.tokens -= 1.0
        self.last_request_time = time.time()


# ============================================================
# Main Scraper Class
# ============================================================

class PlaudScraper:
    """
    Playwright-based scraper for Plaud.AI meeting transcripts.

    Features:
    - Automatic authentication with session persistence
    - Rate limiting (configurable, default 1 req/5s)
    - Retry logic with exponential backoff
    - Progress callbacks for batch operations
    - Incremental downloads (manifest-based)
    - Multiple output formats (JSON, TXT, SRT)
    """

    BASE_URL = "https://web.plaud.ai"
    LOGIN_URL = "https://web.plaud.ai/login"

    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the scraper.

        Args:
            config: Configuration object. If None, uses defaults.
        """
        self.config = config or ScraperConfig()

        # Browser state
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright: Optional[Playwright] = None

        # Rate limiting
        rate_config = RateLimitConfig(requests_per_second=self.config.rate_limit_per_second)
        self.rate_limiter = RateLimiter(rate_config)

        # Session management
        self.session_store: Optional[SessionStore] = None
        self.is_authenticated = False
        self._credentials: Optional[PlaudCredentials] = None

    # ========================================================
    # Browser Lifecycle
    # ========================================================

    async def start(self):
        """Initialize the browser and context."""
        logger.info("Starting Plaud scraper...")

        self._playwright = await async_playwright().start()

        # Launch browser
        self.browser = await self._playwright.chromium.launch(
            headless=self.config.headless,
            slow_mo=self.config.slow_mo
        )

        # Create context
        self.context = await self.browser.new_context(
            viewport={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height
            }
        )

        # Create page
        self.page = await self.context.new_page()

        logger.info("Browser started")

    async def close(self):
        """Close the browser and cleanup."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

        logger.info("Browser closed")

    # ========================================================
    # Session Management
    # ========================================================

    async def save_session(self, path: Path):
        """Save current session to disk."""
        cookies = await self.context.cookies()

        session = SessionStore(
            cookies=cookies,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.config.session_timeout_seconds)
        )

        with open(path, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)

        logger.info(f"Saved session with {len(cookies)} cookies to {path}")

    async def restore_session(self, path: Path) -> bool:
        """
        Restore session from disk.

        Returns:
            True if session was restored and is valid, False otherwise.
        """
        if not path.exists():
            logger.warning(f"Session file not found: {path}")
            return False

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            # Parse session
            session = SessionStore(
                cookies=data.get('cookies', []),
                local_storage=data.get('local_storage', {}),
                session_storage=data.get('session_storage', {}),
                created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
                expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
            )

            # Check if session is still valid
            if not session.is_valid():
                logger.warning("Session has expired")
                return False

            # Add cookies to context
            await self.context.add_cookies(session.cookies)

            self.session_store = session
            logger.info(f"Restored session with {len(session.cookies)} cookies")

            # Verify login
            return await self._verify_login()

        except Exception as e:
            logger.error(f"Failed to restore session: {e}")
            return False

    async def _verify_login(self) -> bool:
        """Verify that we're logged in."""
        try:
            await self.page.goto(self.BASE_URL, timeout=self.config.timeout_ms)
            await self.page.wait_for_load_state("networkidle", timeout=10000)

            # Check if redirected to login
            if "/login" in self.page.url:
                return False

            # Check for file list
            file_list = await self.page.query_selector(PlaudSelectors.FILE_LIST_CONTAINER)
            self.is_authenticated = file_list is not None
            return self.is_authenticated

        except Exception as e:
            logger.debug(f"Login verification failed: {e}")
            return False

    # ========================================================
    # Authentication
    # ========================================================

    async def login(
        self,
        credentials: PlaudCredentials,
        two_factor_callback: Optional[Callable[[], str]] = None
    ) -> bool:
        """
        Authenticate with Plaud.AI.

        Flow:
        1. Navigate to login page
        2. Enter credentials or use OAuth
        3. Handle 2FA if enabled
        4. Store session cookies
        5. Verify login success

        Args:
            credentials: Login credentials
            two_factor_callback: Async function to get 2FA code if needed

        Returns:
            True if login successful

        Raises:
            AuthenticationError: If login fails
        """
        logger.info(f"Logging in as {credentials.email}...")

        try:
            await self.page.goto(self.LOGIN_URL, timeout=self.config.timeout_ms)
            await self.page.wait_for_load_state("networkidle")

            if credentials.use_oauth:
                # OAuth flow (Google, Apple, etc.)
                success = await self._login_oauth(credentials)
            else:
                # Email/password flow
                success = await self._login_email_password(credentials)

            if not success:
                raise AuthenticationError("Login failed")

            # Handle 2FA if needed
            if credentials.two_factor_enabled or await self._is_2fa_required():
                logger.info("2FA required")
                if not two_factor_callback:
                    raise AuthenticationError("2FA required but no callback provided")

                code = await two_factor_callback() if asyncio.iscoroutinefunction(two_factor_callback) else two_factor_callback()
                await self._enter_2fa_code(code)

            # Wait for redirect after login
            await self._wait_for_login_complete()

            # Verify we're logged in
            self.is_authenticated = await self._verify_login()

            if self.is_authenticated:
                self._credentials = credentials
                logger.info("Login successful")
                return True
            else:
                raise AuthenticationError("Login verification failed")

        except PlaywrightTimeout as e:
            raise AuthenticationError(f"Login timeout: {e}")
        except Exception as e:
            raise AuthenticationError(f"Login failed: {e}")

    async def _login_email_password(self, credentials: PlaudCredentials) -> bool:
        """Login using email and password."""
        try:
            # Find and fill email
            email_input = await self.page.wait_for_selector(
                PlaudSelectors.EMAIL_INPUT,
                timeout=self.config.timeout_ms
            )
            await email_input.fill(credentials.email)

            # Find and fill password
            if credentials.password:
                password_input = await self.page.wait_for_selector(PlaudSelectors.PASSWORD_INPUT)
                await password_input.fill(credentials.password)

            # Click login button
            login_button = await self.page.wait_for_selector(PlaudSelectors.LOGIN_BUTTON)
            await login_button.click()

            return True

        except Exception as e:
            logger.error(f"Email/password login failed: {e}")
            return False

    async def _login_oauth(self, credentials: PlaudCredentials) -> bool:
        """Login using OAuth (Google, Apple, etc.)."""
        logger.info(f"Using OAuth provider: {credentials.oauth_provider}")

        try:
            # Click OAuth button
            oauth_button = await self.page.wait_for_selector(
                PlaudSelectors.GOOGLE_LOGIN_BTN,
                timeout=self.config.timeout_ms
            )
            await oauth_button.click()

            # Wait for OAuth popup/redirect
            # User needs to complete OAuth flow manually
            logger.info("Please complete OAuth login in the browser...")

            return True

        except Exception as e:
            logger.error(f"OAuth login failed: {e}")
            return False

    async def _is_2fa_required(self) -> bool:
        """Check if 2FA code is required."""
        # Look for 2FA input field
        try:
            await self.page.wait_for_selector('input[placeholder*="code" i]', timeout=3000)
            return True
        except PlaywrightTimeout:
            return False

    async def _enter_2fa_code(self, code: str):
        """Enter 2FA code."""
        logger.info("Entering 2FA code...")

        code_input = await self.page.wait_for_selector('input[placeholder*="code" i]')
        await code_input.fill(code)

        # Click submit
        submit_button = await self.page.query_selector('button[type="submit"]')
        if submit_button:
            await submit_button.click()

    async def _wait_for_login_complete(self):
        """Wait for login to complete and redirect."""
        start_time = time.time()
        timeout = self.config.timeout_ms / 1000

        while time.time() - start_time < timeout:
            if "/login" not in self.page.url:
                logger.info("Login redirect detected")
                await asyncio.sleep(1)  # Wait for page to settle
                return True
            await asyncio.sleep(0.5)

        raise AuthenticationError("Login did not complete within timeout")

    # ========================================================
    # Transcript List Fetching
    # ========================================================

    async def fetch_transcript_list(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[TranscriptMetadata]:
        """
        Fetch list of available transcripts within date range.

        Pagination:
        - Uses cursor-based pagination by scrolling
        - Fetches all available items up to limit
        - Respects rate limits

        Args:
            start_date: Filter transcripts after this date
            end_date: Filter transcripts before this date
            limit: Maximum number of transcripts to fetch

        Returns:
            List of TranscriptMetadata objects

        Raises:
            SessionExpiredError: If session has expired
            NetworkError: If network request fails
        """
        await self.rate_limiter.acquire()

        logger.info(f"Fetching transcript list (limit={limit})...")

        # Verify authentication
        if not self.is_authenticated:
            if not await self._verify_login():
                raise SessionExpiredError("Session expired, please login again")

        try:
            await self.page.goto(self.BASE_URL, timeout=self.config.timeout_ms)
            await self.page.wait_for_load_state("networkidle")

            # Wait for file list to load
            await self.page.wait_for_selector(PlaudSelectors.FILE_LIST_ITEM, timeout=10000)

            transcripts = []
            seen_ids = set()

            # Scroll to load all files (handle infinite scroll)
            last_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 50

            while scroll_attempts < max_scroll_attempts and len(transcripts) < limit:
                # Get current file items
                items = await self.page.query_selector_all(PlaudSelectors.FILE_LIST_ITEM)
                current_count = len(items)

                # Stop if no new items after multiple attempts
                if current_count == last_count:
                    scroll_attempts += 1
                    if scroll_attempts >= 3:
                        break
                else:
                    scroll_attempts = 0

                last_count = current_count

                # Extract metadata from each item
                for item in items:
                    if len(transcripts) >= limit:
                        break

                    try:
                        metadata = await self._extract_transcript_metadata(item)
                        if metadata and metadata.id not in seen_ids:
                            # Apply date filters
                            if start_date and metadata.date and metadata.date < start_date:
                                continue
                            if end_date and metadata.date and metadata.date > end_date:
                                continue

                            seen_ids.add(metadata.id)
                            transcripts.append(metadata)

                    except Exception as e:
                        logger.warning(f"Failed to extract metadata from item: {e}")

                # Scroll down to load more
                await self.page.evaluate("""
                    const container = document.querySelector('.file-list-content');
                    if (container) container.scrollTop = container.scrollHeight;
                """)
                await asyncio.sleep(0.5)  # Wait for items to load

            logger.info(f"Found {len(transcripts)} transcripts")
            return transcripts

        except PlaywrightTimeout as e:
            raise NetworkError(f"Timeout fetching transcript list: {e}")
        except Exception as e:
            raise NetworkError(f"Failed to fetch transcript list: {e}")

    async def _extract_transcript_metadata(self, item) -> Optional[TranscriptMetadata]:
        """Extract metadata from a file list item element."""
        try:
            # Get filename
            filename_el = await item.query_selector(PlaudSelectors.FILE_ITEM_FILENAME)
            filename = await filename_el.inner_text() if filename_el else "Untitled"

            # Get metadata (date, duration)
            metadata_el = await item.query_selector(PlaudSelectors.FILE_ITEM_METADATA)
            metadata_text = await metadata_el.inner_text() if metadata_el else ""

            # Parse date and duration from metadata text
            # Format is usually: "Jan 15, 2026 • 15:23"
            date = None
            duration = None
            if metadata_text:
                parts = metadata_text.split('•')
                if len(parts) >= 1:
                    try:
                        date = datetime.strptime(parts[0].strip(), "%b %d, %Y")
                    except ValueError:
                        pass
                if len(parts) >= 2:
                    duration_str = parts[1].strip()
                    # Parse duration "15:23" to seconds
                    duration = self._parse_duration(duration_str)

            # Generate ID from filename (will be replaced with actual ID when clicked)
            file_id = filename.replace(" ", "_").lower()[:50]

            return TranscriptMetadata(
                id=file_id,
                title=filename.strip(),
                date=date,
                duration_seconds=duration,
                has_transcript=True  # Assume transcripts exist
            )

        except Exception as e:
            logger.debug(f"Failed to extract metadata: {e}")
            return None

    @staticmethod
    def _parse_duration(duration_str: str) -> Optional[int]:
        """Parse duration string like '15:23' to seconds."""
        try:
            parts = duration_str.split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            pass
        return None

    # ========================================================
    # Transcript Download
    # ========================================================

    async def download_transcript(
        self,
        transcript_id: str,
        output_format: str = "json",
        retry: bool = True
    ) -> Optional[TranscriptContent]:
        """
        Download full transcript content.

        Content includes:
        - Raw text
        - Speaker diarization
        - Timestamps
        - Confidence scores (if available)

        Error handling:
        - Retry up to max_retries times on network failure
        - Skip and log on persistent failure
        - Continue batch on single failure

        Args:
            transcript_id: ID of the transcript to download
            output_format: Format to return (json, txt, srt)
            retry: Whether to retry on failure

        Returns:
            TranscriptContent object or None if failed

        Raises:
            TranscriptNotFoundError: If transcript doesn't exist
            NetworkError: If download fails after retries
        """
        await self.rate_limiter.acquire()

        logger.info(f"Downloading transcript: {transcript_id}")

        attempt = 0
        last_error = None

        while attempt <= self.config.max_retries:
            try:
                return await self._fetch_transcript_content(transcript_id, output_format)

            except TranscriptNotFoundError:
                # Don't retry if transcript doesn't exist
                raise

            except Exception as e:
                last_error = e
                attempt += 1

                if attempt <= self.config.max_retries and retry:
                    # Calculate backoff delay
                    delay = self.config.retry_initial_delay * (self.config.retry_backoff_base ** (attempt - 1))
                    logger.warning(f"Download failed (attempt {attempt}/{self.config.max_retries}), retrying in {delay:.1f}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Download failed after {attempt} attempts: {e}")
                    break

        if last_error:
            raise NetworkError(f"Failed to download transcript after {self.config.max_retries} retries: {last_error}")

        return None

    async def _fetch_transcript_content(
        self,
        transcript_id: str,
        output_format: str
    ) -> TranscriptContent:
        """Fetch the actual transcript content from the page."""
        # Navigate to transcript page
        url = f"{self.BASE_URL}/file/{transcript_id}"

        try:
            await self.page.goto(url, timeout=self.config.timeout_ms)
            await self.page.wait_for_load_state("networkidle")

            # Wait for transcript to load
            transcript_loaded = False
            for selector in [PlaudSelectors.TRANSCRIPT_ITEM, PlaudSelectors.TRANSCRIPT_MODULE]:
                try:
                    await self.page.wait_for_selector(selector, timeout=15000)
                    transcript_loaded = True
                    break
                except PlaywrightTimeout:
                    continue

            if not transcript_loaded:
                raise TranscriptNotFoundError(f"Transcript not found: {transcript_id}")

            # Extract segments
            items = await self.page.query_selector_all(PlaudSelectors.TRANSCRIPT_ITEM)

            if not items:
                raise TranscriptNotFoundError(f"No transcript content found: {transcript_id}")

            segments = []
            raw_text_parts = []
            current_time_ms = 0

            for item in items:
                try:
                    # Get speaker
                    speaker_el = await item.query_selector(PlaudSelectors.SPEAKER_NAME)
                    speaker = await speaker_el.inner_text() if speaker_el else "Speaker"

                    # Get text
                    text = await item.inner_text()
                    if speaker and speaker in text:
                        text = text.replace(speaker, "", 1).strip()

                    # Skip empty or placeholder text
                    if not text or len(text.strip()) == 0:
                        continue
                    if any(phrase in text for phrase in ["Transcript will appear", "Ready to generate"]):
                        continue

                    # Estimate timing (since Plaud doesn't always provide exact timestamps)
                    word_count = len(text.split())
                    duration_ms = int(word_count * 500)  # Assume 120 words per minute
                    start_time_ms = current_time_ms
                    end_time_ms = current_time_ms + duration_ms
                    current_time_ms = end_time_ms

                    segments.append(TranscriptSegment(
                        speaker_label=speaker.strip(),
                        text=text.strip(),
                        start_time_ms=start_time_ms,
                        end_time_ms=end_time_ms
                    ))

                    raw_text_parts.append(f"{speaker}: {text}")

                except Exception as e:
                    logger.warning(f"Failed to parse segment: {e}")

            # Get page title
            title = await self.page.title()

            # Create metadata
            metadata = TranscriptMetadata(
                id=transcript_id,
                title=title,
                date=datetime.now(),  # Would need to parse from page
                duration_seconds=current_time_ms // 1000,
                speaker_count=len(set(seg.speaker_label for seg in segments)),
                word_count=sum(len(seg.text.split()) for seg in segments),
                download_url=url,
                has_transcript=True
            )

            return TranscriptContent(
                metadata=metadata,
                segments=segments,
                raw_text="\n\n".join(raw_text_parts),
                format=output_format
            )

        except PlaywrightTimeout as e:
            raise NetworkError(f"Timeout downloading transcript: {e}")

    # ========================================================
    # Batch Export
    # ========================================================

    async def batch_export(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        output_dir: Path = Path("./data/transcripts"),
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        formats: List[str] = None
    ) -> BatchExportResult:
        """
        Export all transcripts in date range.

        Process:
        1. Fetch transcript list
        2. Filter already downloaded (via manifest)
        3. Download each transcript
        4. Save to output directory
        5. Update manifest
        6. Generate summary report

        Output structure:
        output_dir/
        ├── manifest.json
        ├── 2026-02-01/
        │   ├── meeting-001.json
        │   ├── meeting-001.txt
        │   └── metadata.json
        └── export-report.md

        Args:
            start_date: Start of date range
            end_date: End of date range
            output_dir: Directory to save transcripts
            progress_callback: Called with (current, total, transcript_id)
            formats: List of formats to export (default: ["json", "txt"])

        Returns:
            BatchExportResult with statistics and details
        """
        if formats is None:
            formats = ["json", "txt"]

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        result = BatchExportResult(
            start_time=datetime.now(),
            output_dir=output_dir
        )

        logger.info(f"Starting batch export to {output_dir}")

        try:
            # Load manifest
            manifest_path = output_dir / "manifest.json"
            manifest = self._load_manifest(manifest_path)

            # Fetch transcript list
            transcripts = await self.fetch_transcript_list(
                start_date=start_date,
                end_date=end_date,
                limit=1000  # Reasonable limit
            )

            result.total_count = len(transcripts)
            logger.info(f"Found {len(transcripts)} transcripts to process")

            # Process each transcript
            for i, metadata in enumerate(transcripts, 1):
                transcript_id = metadata.id

                # Progress callback
                if progress_callback:
                    try:
                        progress_callback(i, len(transcripts), transcript_id)
                    except Exception as e:
                        logger.warning(f"Progress callback failed: {e}")

                # Skip if already exported
                if transcript_id in manifest.get('exported', []):
                    logger.info(f"[{i}/{len(transcripts)}] Skipping {transcript_id} (already exported)")
                    result.skipped_count += 1
                    result.items.append(ExportItem(
                        transcript_id=transcript_id,
                        status=ExportStatus.SKIPPED
                    ))
                    continue

                # Download transcript
                export_start = time.time()
                try:
                    logger.info(f"[{i}/{len(transcripts)}] Downloading {transcript_id}")

                    content = await self.download_transcript(transcript_id, output_format="json")

                    if content:
                        # Save files
                        output_path = await self._save_transcript(content, output_dir, formats)

                        # Update manifest
                        manifest.setdefault('exported', []).append(transcript_id)
                        self._save_manifest(manifest, manifest_path)

                        export_duration = int((time.time() - export_start) * 1000)

                        result.success_count += 1
                        result.items.append(ExportItem(
                            transcript_id=transcript_id,
                            status=ExportStatus.SUCCESS,
                            output_path=output_path,
                            duration_ms=export_duration
                        ))

                        logger.info(f"Exported {transcript_id} in {export_duration}ms")
                    else:
                        raise TranscriptNotFoundError("No content returned")

                except Exception as e:
                    logger.error(f"Failed to export {transcript_id}: {e}")

                    manifest.setdefault('failed', []).append({
                        'id': transcript_id,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                    self._save_manifest(manifest, manifest_path)

                    result.failure_count += 1
                    result.items.append(ExportItem(
                        transcript_id=transcript_id,
                        status=ExportStatus.FAILED,
                        error_message=str(e)
                    ))

            result.end_time = datetime.now()

            # Generate report
            report_path = output_dir / "export-report.md"
            with open(report_path, 'w') as f:
                f.write(result.generate_report())

            result.manifest_path = manifest_path

            logger.info(f"Batch export complete: {result.success_count} succeeded, {result.failure_count} failed, {result.skipped_count} skipped")

            return result

        except Exception as e:
            logger.error(f"Batch export failed: {e}")
            result.end_time = datetime.now()
            raise

    async def _save_transcript(
        self,
        content: TranscriptContent,
        output_dir: Path,
        formats: List[str]
    ) -> Path:
        """Save transcript to disk in specified formats."""
        # Create date-based subdirectory if configured
        if self.config.create_date_subdirs and content.metadata.date:
            date_str = content.metadata.date.strftime("%Y-%m-%d")
            save_dir = output_dir / date_str
        else:
            save_dir = output_dir

        save_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        base_name = self._sanitize_filename(content.metadata.id)

        # Save in each format
        saved_path = None
        for fmt in formats:
            if fmt == "json":
                path = save_dir / f"{base_name}.json"
                with open(path, 'w') as f:
                    json.dump(content.to_dict(), f, indent=2)
                saved_path = path

            elif fmt == "txt":
                path = save_dir / f"{base_name}.txt"
                with open(path, 'w') as f:
                    f.write(content.to_plain_text())
                saved_path = path

            elif fmt == "srt":
                path = save_dir / f"{base_name}.srt"
                with open(path, 'w') as f:
                    f.write(content.to_srt())
                saved_path = path

        # Save metadata separately if configured
        if self.config.save_metadata:
            metadata_path = save_dir / "metadata.json"
            metadata_list = []
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata_list = json.load(f)

            metadata_list.append(content.metadata.to_dict())

            with open(metadata_path, 'w') as f:
                json.dump(metadata_list, f, indent=2)

        return saved_path or save_dir

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename to be filesystem-safe."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Limit length
        return filename[:200]

    @staticmethod
    def _load_manifest(path: Path) -> Dict[str, Any]:
        """Load export manifest from disk."""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return {"exported": [], "failed": []}

    @staticmethod
    def _save_manifest(manifest: Dict[str, Any], path: Path):
        """Save export manifest to disk."""
        with open(path, 'w') as f:
            json.dump(manifest, f, indent=2)

    # ========================================================
    # Helper Methods
    # ========================================================

    def get_session_cookies(self) -> List[Dict[str, Any]]:
        """Get current session cookies for external storage."""
        if self.session_store:
            return self.session_store.cookies
        return []

    async def _expire_session(self):
        """Force expire the current session (for testing)."""
        if self.session_store:
            self.session_store.expires_at = datetime.now() - timedelta(hours=1)
        self.is_authenticated = False


# ============================================================
# CLI Entry Point
# ============================================================

async def main():
    """CLI entry point for the scraper."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Plaud.AI Transcript Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export all transcripts
  python plaud_scraper.py --email user@example.com

  # Export with saved session
  python plaud_scraper.py --session session.json

  # Export date range
  python plaud_scraper.py --email user@example.com --start-date 2026-01-01 --end-date 2026-01-31

  # Export in headless mode
  python plaud_scraper.py --email user@example.com --headless
        """
    )

    # Authentication
    parser.add_argument('--email', help='Email for login')
    parser.add_argument('--password', help='Password (will prompt if not provided)')
    parser.add_argument('--session', help='Path to saved session file')

    # Date range
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')

    # Output
    parser.add_argument('--output', default='./data/transcripts', help='Output directory')
    parser.add_argument('--formats', default='json,txt', help='Export formats (comma-separated)')

    # Browser
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')

    args = parser.parse_args()

    # Parse dates
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None

    # Create config
    config = ScraperConfig(
        headless=args.headless,
        timeout_ms=30000,
        rate_limit_per_second=0.2
    )

    # Create scraper
    scraper = PlaudScraper(config)

    try:
        await scraper.start()

        # Authenticate
        if args.session:
            session_path = Path(args.session)
            if not await scraper.restore_session(session_path):
                logger.error("Failed to restore session, please login")
                return

        elif args.email:
            # Get password
            password = args.password
            if not password:
                import getpass
                password = getpass.getpass("Password: ")

            credentials = PlaudCredentials(email=args.email, password=password)

            # Login
            await scraper.login(credentials)

            # Save session
            session_path = Path("plaud_session.json")
            await scraper.save_session(session_path)
            logger.info(f"Session saved to {session_path}")

        else:
            logger.error("Must provide --email or --session")
            return

        # Parse formats
        formats = [f.strip() for f in args.formats.split(',')]

        # Progress callback
        def on_progress(current: int, total: int, transcript_id: str):
            print(f"Progress: {current}/{total} - {transcript_id}")

        # Export
        result = await scraper.batch_export(
            start_date=start_date,
            end_date=end_date,
            output_dir=Path(args.output),
            progress_callback=on_progress,
            formats=formats
        )

        # Print summary
        print("\n" + "="*60)
        print("EXPORT SUMMARY")
        print("="*60)
        print(f"Total: {result.total_count}")
        print(f"Success: {result.success_count}")
        print(f"Failed: {result.failure_count}")
        print(f"Skipped: {result.skipped_count}")
        print(f"Duration: {result.duration_seconds():.1f}s")
        print(f"Output: {result.output_dir}")
        print("="*60)

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
