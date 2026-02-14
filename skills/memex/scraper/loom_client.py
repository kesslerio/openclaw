"""
Loom Transcript Client

Fetches transcripts from Loom share URLs by parsing the Apollo GraphQL
state embedded in the page HTML. No API key needed for public/shared videos.

Loom embeds window.__APOLLO_STATE__ in the page which contains:
  - VideoTranscriptDetails with signed CDN URLs for transcript JSON and VTT
  - Video metadata (duration, creator, title, etc.)
  - Schema.org JSON-LD with additional metadata

Output format matches Plaud transcripts for seamless FAISS indexing:
  loom_transcripts/
    Video Title_abc12345/
      metadata.json
      transcript.json
      transcript.txt
      notes.md

Usage:
    # Single video
    python -m memex.scraper.loom_client https://www.loom.com/share/abc123

    # Bulk from file (one URL per line)
    python -m memex.scraper.loom_client --file urls.txt

    # List already imported
    python -m memex.scraper.loom_client --list
"""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

SCRAPER_DIR = Path(__file__).parent
MANIFEST_PATH = SCRAPER_DIR / "loom_manifest.json"
DEFAULT_OUTPUT = SCRAPER_DIR.parent.parent / "data" / "loom_transcripts"

# Regex to extract video ID from various Loom URL formats
LOOM_URL_RE = re.compile(r"loom\.com/(?:share|embed|v)/([a-f0-9]+)")

# User-Agent to avoid bot detection
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def extract_video_id(url: str) -> Optional[str]:
    """Extract the video ID from a Loom share/embed/v URL."""
    match = LOOM_URL_RE.search(url)
    return match.group(1) if match else None


def _safe_dirname(title: str, video_id: str) -> str:
    """Create a safe directory name from title + video_id prefix (matches Plaud pattern)."""
    safe = re.sub(r'[<>:"/\\|?*]', "_", title)
    safe = safe.strip(". ")
    if len(safe) > 80:
        safe = safe[:80].rstrip()
    return f"{safe}_{video_id[:8]}"


def _parse_apollo_state(html: str) -> Optional[Dict[str, Any]]:
    """Extract window.__APOLLO_STATE__ from page HTML."""
    # Look for the Apollo state assignment in script tags
    pattern = r"window\.__APOLLO_STATE__\s*=\s*(\{.+?\});\s*(?:</script>|window\.)"
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        # Try a more lenient pattern
        pattern2 = r"__APOLLO_STATE__\s*=\s*(\{.+?\})\s*;"
        match = re.search(pattern2, html, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Apollo state JSON: {e}")
        return None


def _parse_schema_org(html: str) -> Optional[Dict[str, Any]]:
    """Extract schema.org JSON-LD structured data from the page."""
    pattern = r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        return None
    try:
        # strict=False to handle control characters in Loom's JSON-LD
        return json.loads(match.group(1), strict=False)
    except json.JSONDecodeError:
        return None


def _parse_og_meta(html: str) -> Dict[str, str]:
    """Extract Open Graph meta tags from the page."""
    tags = {}
    for match in re.finditer(r'<meta\s+property="og:(\w+)"\s+content="([^"]*)"', html):
        tags[match.group(1)] = match.group(2)
    # Also try reversed attribute order
    for match in re.finditer(r'<meta\s+content="([^"]*)"\s+property="og:(\w+)"', html):
        tags[match.group(2)] = match.group(1)
    return tags


def _find_transcript_details(apollo_state: Dict) -> Optional[Dict]:
    """Find VideoTranscriptDetails in the Apollo state."""
    for key, value in apollo_state.items():
        if key.startswith("VideoTranscriptDetails:") and isinstance(value, dict):
            return value
    return None


def _find_video_details(apollo_state: Dict, video_id: str) -> Optional[Dict]:
    """Find the video object in the Apollo state."""
    # Try exact match first
    for key_prefix in ["RegularUserVideo:", "Video:"]:
        key = f"{key_prefix}{video_id}"
        if key in apollo_state:
            return apollo_state[key]

    # Fallback: search for any video object containing this ID
    for key, value in apollo_state.items():
        if isinstance(value, dict) and value.get("s3_id") == video_id:
            return value
    return None


def _parse_iso_duration(iso_dur: str) -> int:
    """Convert ISO 8601 duration (PT110S, PT1M30S) to milliseconds."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_dur or "")
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return (hours * 3600 + minutes * 60 + seconds) * 1000


def _parse_transcript_json(data: Any) -> List[Dict]:
    """
    Parse Loom transcript JSON into Plaud-compatible segments.

    Loom's primary format (schemaVersion 1.1.x):
        {"phrases": [{"ts": float_secs, "value": "text", "ranges": [...]}], "schemaVersion": "1.1.3"}

    Also handles Whisper and other fallback formats.
    """
    segments = []

    if isinstance(data, dict):
        # Loom phrases format (primary, discovered Feb 2026)
        if "phrases" in data:
            phrases = data["phrases"]
            for i, phrase in enumerate(phrases):
                ts = float(phrase.get("ts", 0))
                value = (phrase.get("value") or "").strip()
                if not value:
                    continue
                # Estimate end time from next phrase or add 5 seconds
                if i + 1 < len(phrases):
                    end_ts = float(phrases[i + 1].get("ts", ts + 5))
                else:
                    end_ts = ts + 5
                segments.append({
                    "start_time": int(ts * 1000),
                    "end_time": int(end_ts * 1000),
                    "content": value,
                    "speaker": "Speaker",
                    "original_speaker": "Speaker",
                })
            return segments

        # Whisper format: {"segments": [{"start": 0.0, "end": 5.0, "text": "..."}]}
        if "segments" in data:
            for seg in data["segments"]:
                segments.append({
                    "start_time": int(float(seg.get("start", 0)) * 1000),
                    "end_time": int(float(seg.get("end", 0)) * 1000),
                    "content": (seg.get("text") or "").strip(),
                    "speaker": seg.get("speaker", "Speaker"),
                    "original_speaker": seg.get("speaker", "Speaker"),
                })
            return segments

    elif isinstance(data, list):
        # Direct list of segments
        for seg in data:
            if isinstance(seg, dict):
                start_raw = seg.get("start_time", seg.get("start", 0))
                end_raw = seg.get("end_time", seg.get("end", 0))
                # Convert float seconds to ms if needed
                start_ms = int(float(start_raw) * 1000) if isinstance(start_raw, float) else int(start_raw)
                end_ms = int(float(end_raw) * 1000) if isinstance(end_raw, float) else int(end_raw)
                segments.append({
                    "start_time": start_ms,
                    "end_time": end_ms,
                    "content": (seg.get("content") or seg.get("text") or "").strip(),
                    "speaker": seg.get("speaker", "Speaker"),
                    "original_speaker": seg.get("speaker", "Speaker"),
                })
        return segments

    return segments


def _parse_vtt(vtt_text: str) -> List[Dict]:
    """Parse WebVTT captions into Plaud-compatible segments."""
    segments = []
    blocks = vtt_text.strip().split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")
        # Find the timestamp line
        timestamp_line = None
        text_lines = []
        for line in lines:
            if "-->" in line:
                timestamp_line = line
            elif timestamp_line and line.strip():
                text_lines.append(line.strip())

        if not timestamp_line or not text_lines:
            continue

        # Parse timestamps: "00:00:01.500 --> 00:00:05.200"
        ts_match = re.match(
            r"(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{3})",
            timestamp_line,
        )
        if not ts_match:
            continue

        def ts_to_ms(ts: str) -> int:
            ts = ts.replace(",", ".")
            parts = ts.split(":")
            h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
            return int((h * 3600 + m * 60 + s) * 1000)

        segments.append({
            "start_time": ts_to_ms(ts_match.group(1)),
            "end_time": ts_to_ms(ts_match.group(2)),
            "content": " ".join(text_lines),
            "speaker": "Speaker",
            "original_speaker": "Speaker",
        })

    return segments


class LoomClient:
    """Fetches Loom video metadata and transcripts from share pages."""

    def __init__(self):
        self.http = httpx.Client(
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            timeout=30.0,
        )

    def close(self):
        self.http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def fetch_video(self, url: str) -> Dict[str, Any]:
        """
        Fetch video metadata and transcript from a Loom share URL.

        Returns dict with:
            video_id, title, duration_ms, date, creator,
            transcript_segments, transcript_text, loom_url
        """
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")

        share_url = f"https://www.loom.com/share/{video_id}"
        logger.info(f"Fetching Loom page: {share_url}")

        resp = self.http.get(share_url)
        resp.raise_for_status()
        html = resp.text

        # Parse all available data sources
        apollo_state = _parse_apollo_state(html)
        schema_org = _parse_schema_org(html)
        og_tags = _parse_og_meta(html)

        if not apollo_state:
            raise RuntimeError(
                f"Could not find Apollo state in page HTML. "
                f"The video may be private or the page structure has changed."
            )

        # Extract video metadata
        video_details = _find_video_details(apollo_state, video_id)
        transcript_details = _find_transcript_details(apollo_state)

        # Build title from multiple sources
        title = (
            (video_details or {}).get("name")
            or og_tags.get("title")
            or (schema_org or {}).get("name")
            or f"Loom Video {video_id[:8]}"
        )

        # Build duration
        duration_ms = 0
        if video_details and video_details.get("playable_duration"):
            duration_ms = int(float(video_details["playable_duration"]) * 1000)
        elif schema_org and schema_org.get("duration"):
            duration_ms = _parse_iso_duration(schema_org["duration"])

        # Build date (upload date)
        date_str = None
        if schema_org and schema_org.get("uploadDate"):
            try:
                dt = datetime.fromisoformat(schema_org["uploadDate"].replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                pass
        if not date_str and video_details and video_details.get("createdAt"):
            try:
                dt = datetime.fromisoformat(video_details["createdAt"].replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                pass
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        # Build creator name
        creator = "Unknown"
        if video_details:
            owner_ref = video_details.get("owner")
            if isinstance(owner_ref, dict) and "__ref" in owner_ref:
                owner_key = owner_ref["__ref"]
                owner_data = apollo_state.get(owner_key, {})
                creator = owner_data.get("display_name") or owner_data.get("first_name") or "Unknown"

        # Build start_time (epoch ms)
        start_time_ms = 0
        if schema_org and schema_org.get("uploadDate"):
            try:
                dt = datetime.fromisoformat(schema_org["uploadDate"].replace("Z", "+00:00"))
                start_time_ms = int(dt.timestamp() * 1000)
            except (ValueError, TypeError):
                pass

        # Fetch transcript
        transcript_segments = []
        transcript_source = None

        if transcript_details:
            status = transcript_details.get("transcription_status")
            if status != "success":
                logger.warning(f"Transcript status is '{status}', may not be available")

            # Try source_url first (signed CDN URL for transcript JSON)
            source_url = transcript_details.get("source_url")
            if source_url:
                try:
                    logger.info("Fetching transcript JSON from signed CDN URL")
                    t_resp = self.http.get(source_url)
                    t_resp.raise_for_status()
                    transcript_data = t_resp.json()
                    transcript_segments = _parse_transcript_json(transcript_data)
                    transcript_source = "json"
                    logger.info(f"Got {len(transcript_segments)} segments from transcript JSON")
                except Exception as e:
                    logger.warning(f"Failed to fetch transcript JSON: {e}")

            # Fallback to captions VTT
            if not transcript_segments:
                captions_url = transcript_details.get("captions_source_url")
                if captions_url:
                    try:
                        logger.info("Fetching captions VTT from signed CDN URL")
                        c_resp = self.http.get(captions_url)
                        c_resp.raise_for_status()
                        transcript_segments = _parse_vtt(c_resp.text)
                        transcript_source = "vtt"
                        logger.info(f"Got {len(transcript_segments)} segments from VTT captions")
                    except Exception as e:
                        logger.warning(f"Failed to fetch VTT captions: {e}")
        else:
            logger.warning("No VideoTranscriptDetails found in Apollo state")

        if not transcript_segments:
            logger.warning(f"No transcript available for video {video_id}")

        # Build plain text
        transcript_text = "\n".join(
            f"{seg['speaker']}: {seg['content']}" for seg in transcript_segments
        )

        return {
            "video_id": video_id,
            "title": title,
            "duration_ms": duration_ms,
            "date": date_str,
            "start_time_ms": start_time_ms,
            "creator": creator,
            "transcript_segments": transcript_segments,
            "transcript_text": transcript_text,
            "transcript_source": transcript_source,
            "loom_url": share_url,
        }


class LoomExporter:
    """Exports Loom video transcripts to Plaud-compatible directory format."""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or DEFAULT_OUTPUT
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        if MANIFEST_PATH.exists():
            with open(MANIFEST_PATH) as f:
                return json.load(f)
        return {}

    def _save_manifest(self):
        with open(MANIFEST_PATH, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def is_exported(self, video_id: str) -> bool:
        return video_id in self.manifest

    def export_url(self, url: str, force: bool = False) -> Optional[str]:
        """
        Export a single Loom video to a local transcript directory.

        Returns the directory name if successful, None if skipped or failed.
        """
        video_id = extract_video_id(url)
        if not video_id:
            logger.error(f"Invalid Loom URL: {url}")
            return None

        if not force and self.is_exported(video_id):
            logger.info(f"Already exported: {video_id}")
            return None

        with LoomClient() as client:
            try:
                video_data = client.fetch_video(url)
            except Exception as e:
                logger.error(f"Failed to fetch {url}: {e}")
                return None

        if not video_data["transcript_segments"]:
            logger.warning(f"No transcript for {video_data['title']} ({video_id}), saving metadata only")

        dir_name = _safe_dirname(video_data["title"], video_id)
        dir_path = self.output_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

        # Save metadata.json (Plaud-compatible schema)
        metadata = {
            "file_id": f"loom_{video_id}",
            "filename": video_data["title"],
            "duration_ms": video_data["duration_ms"],
            "start_time": video_data["start_time_ms"],
            "source": "loom",
            "loom_url": video_data["loom_url"],
            "creator": video_data["creator"],
            "exported_at": datetime.now().isoformat(),
        }
        with open(dir_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Save transcript.json (Plaud-compatible segment format)
        with open(dir_path / "transcript.json", "w") as f:
            json.dump(video_data["transcript_segments"], f, indent=2)

        # Save transcript.txt (plain text)
        with open(dir_path / "transcript.txt", "w") as f:
            f.write(video_data["transcript_text"])

        # Save notes.md (placeholder)
        with open(dir_path / "notes.md", "w") as f:
            f.write(f"# {video_data['title']}\n\n")
            f.write(f"*Source: Loom*\n")
            f.write(f"*Creator: {video_data['creator']}*\n")
            f.write(f"*Date: {video_data['date']}*\n")
            f.write(f"*Duration: {video_data['duration_ms'] // 1000}s*\n\n")
            if not video_data["transcript_segments"]:
                f.write("(No transcript available for this Loom video)\n")

        # Update manifest
        self.manifest[video_id] = {
            "title": video_data["title"],
            "exported_at": metadata["exported_at"],
            "dir_name": dir_name,
            "segments": len(video_data["transcript_segments"]),
            "transcript_source": video_data["transcript_source"],
        }
        self._save_manifest()

        seg_count = len(video_data["transcript_segments"])
        logger.info(f"Exported: {dir_name} ({seg_count} segments)")
        return dir_name

    def export_file(self, urls_file: Path, force: bool = False, delay: float = 2.0) -> Dict:
        """Export multiple Loom videos from a text file (one URL per line)."""
        urls = []
        with open(urls_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)

        stats = {"exported": 0, "skipped": 0, "failed": 0, "no_transcript": 0}
        logger.info(f"Processing {len(urls)} URLs from {urls_file}")

        for i, url in enumerate(urls):
            logger.info(f"[{i+1}/{len(urls)}] {url}")
            result = self.export_url(url, force=force)
            if result is None:
                vid = extract_video_id(url)
                if vid and self.is_exported(vid):
                    stats["skipped"] += 1
                else:
                    stats["failed"] += 1
            else:
                stats["exported"] += 1

            if i < len(urls) - 1:
                time.sleep(delay)

        logger.info(f"Batch export complete: {stats}")
        return stats

    def list_exported(self) -> List[Dict]:
        """List all exported Loom videos."""
        entries = []
        for vid, info in sorted(self.manifest.items(), key=lambda x: x[1].get("exported_at", "")):
            entries.append({
                "video_id": vid,
                "title": info.get("title", "?"),
                "dir_name": info.get("dir_name", "?"),
                "segments": info.get("segments", 0),
                "exported_at": info.get("exported_at", "?"),
            })
        return entries


def main():
    """CLI entry point."""
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Loom Transcript Client - fetch and export Loom video transcripts"
    )
    parser.add_argument("url", nargs="?", help="Loom share URL to export")
    parser.add_argument("--file", type=str, help="Text file with Loom URLs (one per line)")
    parser.add_argument("--list", action="store_true", help="List already exported videos")
    parser.add_argument("--force", action="store_true", help="Re-export even if already done")
    parser.add_argument("--output", type=str, help="Output directory", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--delay", type=float, help="Delay between requests (seconds)", default=2.0)

    args = parser.parse_args()
    exporter = LoomExporter(output_dir=Path(args.output))

    if args.list:
        entries = exporter.list_exported()
        if not entries:
            print("No Loom videos exported yet.")
            return
        print(f"\n{'Title':<50} {'Segments':>8}  {'Exported'}")
        print("-" * 80)
        for e in entries:
            print(f"{e['title'][:50]:<50} {e['segments']:>8}  {e['exported_at'][:19]}")
        print(f"\nTotal: {len(entries)} videos")
        return

    if args.file:
        stats = exporter.export_file(Path(args.file), force=args.force, delay=args.delay)
        print(f"\nResults: {stats}")
        return

    if args.url:
        result = exporter.export_url(args.url, force=args.force)
        if result:
            print(f"\nExported to: {args.output}/{result}")
        else:
            print("\nExport failed or skipped (use --force to re-export)")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
