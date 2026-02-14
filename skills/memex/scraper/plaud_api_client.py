"""
Plaud.AI Direct API Client

Uses the real REST API at api.plaud.ai to export transcripts.
Auth via JWT bearer token extracted from browser session (CDP or cookies).

API endpoints (discovered Feb 8, 2026):
  GET  /file/simple/web?skip=0&limit=N&is_trash=2&sort_by=start_time&is_desc=true
  GET  /file/detail/{file_id}   → content_list with pre-signed S3 URLs
  GET  /ai/query_note           → summaries (file-id header)
  GET  /user/me                 → user profile
  GET  /filetag/                → folder tags

Content types in file detail:
  transaction    → transcript segments (speaker, content, start_time, end_time)
  outline        → topic outline
  auto_sum_note  → AI summary
  sum_multi_note → extended meeting minutes
"""

import gzip
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://api.plaud.ai"
CDP_URL = "http://localhost:18800"
SCRAPER_DIR = Path(__file__).parent
AUTH_PATH = SCRAPER_DIR / "plaud_auth.json"
COOKIES_PATH = SCRAPER_DIR / "plaud_cookies.json"
MANIFEST_PATH = SCRAPER_DIR / "export_manifest.json"
DEFAULT_OUTPUT = SCRAPER_DIR.parent.parent / "data" / "plaud_transcripts"


def refresh_jwt_via_cdp() -> Optional[Dict[str, str]]:
    """Extract a fresh JWT by connecting to Chrome via CDP and intercepting API calls."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("Playwright not installed, cannot refresh JWT via CDP")
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0]

            captured = {}

            def on_request(request):
                if "api.plaud.ai" in request.url and "guardian" not in request.url:
                    h = request.headers
                    if "authorization" in h and not captured:
                        captured["authorization"] = h["authorization"]
                        captured["x-pld-tag"] = h.get("x-pld-tag", "")

            page = ctx.new_page()
            page.on("request", on_request)
            page.goto("https://web.plaud.ai/", timeout=30000, wait_until="networkidle")
            time.sleep(3)

            if "/login" in page.url:
                logger.error("Not logged in — Chrome session expired")
                page.close()
                browser.close()
                return None

            # Save cookies too
            cookies = ctx.cookies([
                "https://web.plaud.ai", "https://api.plaud.ai",
                "https://plaud.ai", "https://www.google.com",
            ])
            with open(COOKIES_PATH, "w") as f:
                json.dump(cookies, f, indent=2)

            page.close()
            browser.close()

            if captured:
                captured["extracted_at"] = time.time()
                with open(AUTH_PATH, "w") as f:
                    json.dump(captured, f, indent=2)
                logger.info("Fresh JWT extracted and saved")
                return captured
            else:
                logger.warning("No API requests intercepted — JWT not captured")
                return None
    except Exception as e:
        logger.warning(f"CDP refresh failed: {e}")
        return None


def load_auth() -> Dict[str, str]:
    """Load auth headers from saved file, refreshing via CDP if needed."""
    if AUTH_PATH.exists():
        with open(AUTH_PATH) as f:
            auth = json.load(f)
        # Check if JWT is reasonably fresh (< 24h)
        extracted = auth.get("extracted_at", 0)
        if time.time() - extracted < 86400:
            return {
                "authorization": auth["authorization"],
                "x-pld-tag": auth.get("x-pld-tag", ""),
            }
        logger.info("Auth token older than 24h, refreshing...")

    # Try CDP refresh
    result = refresh_jwt_via_cdp()
    if result:
        return {
            "authorization": result["authorization"],
            "x-pld-tag": result.get("x-pld-tag", ""),
        }

    raise RuntimeError(
        "No valid auth token available. Ensure Chrome is running with "
        "Plaud logged in and CDP port 18800 is accessible."
    )


class PlaudClient:
    """Direct HTTP client for the Plaud.AI REST API."""

    def __init__(self, auth: Optional[Dict[str, str]] = None):
        if auth is None:
            auth = load_auth()
        self.client = httpx.Client(
            base_url=BASE_URL,
            headers={
                "authorization": auth["authorization"],
                "x-pld-tag": auth.get("x-pld-tag", ""),
                "origin": "https://web.plaud.ai",
                "referer": "https://web.plaud.ai/",
                "accept": "application/json",
            },
            timeout=30,
        )

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ------ Core API calls ------

    def get_user(self) -> Dict:
        """Get current user info."""
        resp = self.client.get("/user/me")
        resp.raise_for_status()
        return resp.json()

    def list_files(
        self,
        skip: int = 0,
        limit: int = 99999,
        is_trash: int = 2,
        sort_by: str = "start_time",
        is_desc: bool = True,
    ) -> List[Dict]:
        """List all recording files."""
        resp = self.client.get(
            "/file/simple/web",
            params={
                "skip": skip,
                "limit": limit,
                "is_trash": is_trash,
                "sort_by": sort_by,
                "is_desc": str(is_desc).lower(),
            },
        )
        resp.raise_for_status()
        data = resp.json()
        total = data.get("data_file_total", 0)
        files = data.get("data_file_list", [])
        logger.info(f"Listed {len(files)} files (total on server: {total})")
        return files

    def get_file_detail(self, file_id: str) -> Dict:
        """Get file detail including pre-signed S3 download URLs."""
        resp = self.client.get(f"/file/detail/{file_id}")
        resp.raise_for_status()
        return resp.json().get("data", {})

    def get_notes(self, file_id: str) -> List[Dict]:
        """Get AI-generated notes/summaries for a file."""
        resp = self.client.get("/ai/query_note", headers={"file-id": file_id})
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_tags(self) -> List[Dict]:
        """Get all file tags/folders."""
        resp = self.client.get("/filetag/")
        resp.raise_for_status()
        return resp.json().get("data_filetag_list", [])

    # ------ Content download ------

    @staticmethod
    def download_s3_content(url: str) -> Any:
        """Download content from a pre-signed S3 URL. Handles gzip or plain JSON."""
        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()
        raw = resp.content
        # Try gzip first, fall back to plain JSON
        try:
            raw = gzip.decompress(raw)
        except (gzip.BadGzipFile, OSError):
            pass
        return json.loads(raw)

    def get_transcript(self, file_id: str) -> Optional[List[Dict]]:
        """Get transcript segments for a file."""
        detail = self.get_file_detail(file_id)
        for content in detail.get("content_list", []):
            if content["data_type"] == "transaction" and content.get("data_link"):
                return self.download_s3_content(content["data_link"])
        return None

    def get_outline(self, file_id: str) -> Optional[List[Dict]]:
        """Get topic outline for a file."""
        detail = self.get_file_detail(file_id)
        for content in detail.get("content_list", []):
            if content["data_type"] == "outline" and content.get("data_link"):
                return self.download_s3_content(content["data_link"])
        return None

    def get_summary(self, file_id: str) -> Optional[Dict]:
        """Get AI summary for a file."""
        detail = self.get_file_detail(file_id)
        for content in detail.get("content_list", []):
            if content["data_type"] == "auto_sum_note" and content.get("data_link"):
                return self.download_s3_content(content["data_link"])
        return None


# ------ Transcript formatting ------

def format_transcript_text(segments: List[Dict], include_timestamps: bool = True) -> str:
    """Convert transcript segments to readable plain text."""
    lines = []
    for seg in segments:
        speaker = seg.get("speaker", "Unknown")
        content = seg.get("content", "").strip()
        if not content:
            continue
        if include_timestamps:
            start_ms = seg.get("start_time", 0)
            mins, secs = divmod(start_ms // 1000, 60)
            hours, mins = divmod(mins, 60)
            ts = f"[{hours:02d}:{mins:02d}:{secs:02d}]"
            lines.append(f"{ts} {speaker}: {content}")
        else:
            lines.append(f"{speaker}: {content}")
    return "\n\n".join(lines)


def format_summary_markdown(notes: List[Dict]) -> str:
    """Convert AI notes to markdown."""
    parts = []
    for note in notes:
        raw = note.get("data_content", "")
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
            ai_content = parsed.get("ai_content", "")
            if ai_content:
                tab = note.get("data_tab_name", "Note")
                parts.append(f"# {tab}\n\n{ai_content}")
        except (json.JSONDecodeError, TypeError):
            parts.append(str(raw))
    return "\n\n---\n\n".join(parts)


# ------ Batch exporter ------

class PlaudExporter:
    """Exports all Plaud transcripts to local files."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or DEFAULT_OUTPUT
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict:
        manifest_file = self.output_dir / "manifest.json"
        if manifest_file.exists():
            with open(manifest_file) as f:
                return json.load(f)
        return {"exported": {}, "failed": {}, "last_run": None}

    def _save_manifest(self):
        manifest_file = self.output_dir / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def export_all(
        self,
        limit: int = 0,
        skip_existing: bool = True,
        rate_limit: float = 1.0,
    ) -> Dict[str, int]:
        """
        Export all transcripts.

        Args:
            limit: Max files to export (0 = all)
            skip_existing: Skip files already in manifest
            rate_limit: Seconds between API calls
        """
        stats = {"total": 0, "exported": 0, "skipped": 0, "failed": 0, "no_transcript": 0}

        with PlaudClient() as client:
            # Verify session
            user = client.get_user()
            username = user.get("data_user", {}).get("nickname", "unknown")
            logger.info(f"Authenticated as: {username}")

            # List all files
            files = client.list_files()
            stats["total"] = len(files)

            if limit > 0:
                files = files[:limit]

            for i, file_info in enumerate(files):
                file_id = file_info["id"]
                filename = file_info.get("filename", file_id)

                # Skip already exported
                if skip_existing and file_id in self.manifest["exported"]:
                    stats["skipped"] += 1
                    continue

                try:
                    self._export_one(client, file_id, filename, file_info)
                    stats["exported"] += 1
                    logger.info(
                        f"[{i+1}/{len(files)}] Exported: {filename}"
                    )
                except TranscriptNotAvailable:
                    stats["no_transcript"] += 1
                    logger.debug(f"[{i+1}/{len(files)}] No transcript: {filename}")
                except Exception as e:
                    stats["failed"] += 1
                    self.manifest["failed"][file_id] = {
                        "filename": filename,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                    logger.error(f"[{i+1}/{len(files)}] Failed: {filename}: {e}")

                self._save_manifest()
                if rate_limit > 0:
                    time.sleep(rate_limit)

        self.manifest["last_run"] = datetime.now().isoformat()
        self._save_manifest()
        return stats

    def _export_one(self, client: PlaudClient, file_id: str, filename: str, file_info: Dict):
        """Export a single file's transcript and metadata."""
        # Get file detail (includes S3 URLs)
        detail = client.get_file_detail(file_id)
        content_list = detail.get("content_list", [])

        if not content_list:
            raise TranscriptNotAvailable(f"No content for {file_id}")

        # Create a directory for this file
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in filename)
        file_dir = self.output_dir / f"{safe_name}_{file_id[:8]}"
        file_dir.mkdir(exist_ok=True)

        # Download each content type
        has_transcript = False
        for content in content_list:
            dtype = content["data_type"]
            url = content.get("data_link", "")
            if not url:
                continue

            try:
                data = client.download_s3_content(url)

                if dtype == "transaction":
                    has_transcript = True
                    # Save raw JSON
                    with open(file_dir / "transcript.json", "w") as f:
                        json.dump(data, f, indent=2)
                    # Save plain text
                    with open(file_dir / "transcript.txt", "w") as f:
                        f.write(format_transcript_text(data))

                elif dtype == "outline":
                    with open(file_dir / "outline.json", "w") as f:
                        json.dump(data, f, indent=2)

                elif dtype in ("auto_sum_note", "sum_multi_note"):
                    suffix = "summary" if dtype == "auto_sum_note" else "minutes"
                    with open(file_dir / f"{suffix}.json", "w") as f:
                        json.dump(data, f, indent=2)

            except Exception as e:
                logger.warning(f"Failed to download {dtype} for {file_id}: {e}")

        if not has_transcript:
            raise TranscriptNotAvailable(f"No transcript content for {file_id}")

        # Also get AI notes (inline, no S3)
        try:
            notes = client.get_notes(file_id)
            if notes:
                with open(file_dir / "notes.json", "w") as f:
                    json.dump(notes, f, indent=2)
                md = format_summary_markdown(notes)
                if md.strip():
                    with open(file_dir / "notes.md", "w") as f:
                        f.write(md)
        except Exception as e:
            logger.debug(f"Notes fetch failed for {file_id}: {e}")

        # Save metadata
        meta = {
            "file_id": file_id,
            "filename": filename,
            "duration_ms": file_info.get("duration", detail.get("duration", 0)),
            "start_time": file_info.get("start_time", detail.get("start_time", 0)),
            "scene": file_info.get("scene", detail.get("scene", 0)),
            "serial_number": file_info.get("serial_number", ""),
            "exported_at": datetime.now().isoformat(),
        }
        with open(file_dir / "metadata.json", "w") as f:
            json.dump(meta, f, indent=2)

        # Update manifest
        self.manifest["exported"][file_id] = {
            "filename": filename,
            "dir": str(file_dir),
            "exported_at": datetime.now().isoformat(),
        }


class TranscriptNotAvailable(Exception):
    pass


# ------ CLI ------

def main():
    import argparse
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Plaud.AI Transcript Exporter")
    sub = parser.add_subparsers(dest="cmd")

    # test-auth
    sub.add_parser("test-auth", help="Test authentication")

    # list
    lp = sub.add_parser("list", help="List recordings")
    lp.add_argument("-n", "--limit", type=int, default=20)

    # export-one
    ep1 = sub.add_parser("export-one", help="Export a single transcript")
    ep1.add_argument("file_id", help="File ID to export")

    # export
    ep = sub.add_parser("export", help="Export all transcripts")
    ep.add_argument("-o", "--output", type=str, default=str(DEFAULT_OUTPUT))
    ep.add_argument("-n", "--limit", type=int, default=0, help="Max files (0=all)")
    ep.add_argument("--rate-limit", type=float, default=1.0, help="Seconds between calls")
    ep.add_argument("--include-failed", action="store_true", help="Retry previously failed")

    # refresh-auth
    sub.add_parser("refresh-auth", help="Refresh JWT token via CDP")

    args = parser.parse_args()

    if args.cmd == "test-auth":
        try:
            with PlaudClient() as c:
                user = c.get_user()
                u = user.get("data_user", {})
                print(f"Authenticated as: {u.get('nickname', '?')}")
                print(f"Email: {u.get('email', '?')}")
                print(f"Membership: {u.get('membership_id', '?')}")
                files = c.list_files(limit=1)
                print(f"Files accessible: yes ({len(files)} returned)")
        except Exception as e:
            print(f"Auth failed: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.cmd == "list":
        with PlaudClient() as c:
            files = c.list_files(limit=args.limit)
            for f in files:
                dur_s = f.get("duration", 0) // 1000
                ts = f.get("start_time", 0) // 1000
                dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "?"
                trans = "T" if f.get("is_transcribed") else "-"
                print(f"  {f['id'][:12]}  {dur_s:>5}s  {dt}  {trans}  {f.get('filename', '?')}")

    elif args.cmd == "export-one":
        with PlaudClient() as c:
            detail = c.get_file_detail(args.file_id)
            print(f"File: {detail.get('file_name', '?')}")
            print(f"Content items: {len(detail.get('content_list', []))}")
            transcript = c.get_transcript(args.file_id)
            if transcript:
                print(f"\nTranscript ({len(transcript)} segments):\n")
                print(format_transcript_text(transcript))
            else:
                print("No transcript available for this file.")

    elif args.cmd == "export":
        exporter = PlaudExporter(output_dir=Path(args.output))
        if args.include_failed:
            exporter.manifest["failed"] = {}
        stats = exporter.export_all(limit=args.limit, rate_limit=args.rate_limit)
        print(f"\nExport complete:")
        print(f"  Total files: {stats['total']}")
        print(f"  Exported:    {stats['exported']}")
        print(f"  Skipped:     {stats['skipped']}")
        print(f"  No transcript: {stats['no_transcript']}")
        print(f"  Failed:      {stats['failed']}")
        print(f"  Output:      {args.output}")

    elif args.cmd == "refresh-auth":
        result = refresh_jwt_via_cdp()
        if result:
            print(f"JWT refreshed successfully")
            print(f"Token: {result['authorization'][:60]}...")
        else:
            print("Failed to refresh JWT. Is Chrome running with Plaud logged in?")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
