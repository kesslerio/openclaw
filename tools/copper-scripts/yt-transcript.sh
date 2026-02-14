#!/bin/bash
# yt-transcript.sh — Extract YouTube transcript for free
# Usage: ./scripts/yt-transcript.sh <youtube-url>
# No API key needed. Uses youtube-transcript-api (captions) with yt-dlp fallback.

set -euo pipefail

URL="${1:?Usage: yt-transcript.sh <youtube-url>}"

# Extract video ID from various YouTube URL formats
VIDEO_ID=$(echo "$URL" | sed -E 's/.*[?&]v=([^&]+).*/\1/' | sed -E 's/.*youtu\.be\/([^?]+).*/\1/' | sed -E 's/.*shorts\/([^?]+).*/\1/')

if [ -z "$VIDEO_ID" ] || [ ${#VIDEO_ID} -gt 20 ]; then
  echo "ERROR: Could not extract video ID from: $URL" >&2
  exit 1
fi

echo "Video ID: $VIDEO_ID" >&2

# Method 1: youtube-transcript-api (preferred — fast, no download needed)
python3 -c "
from youtube_transcript_api import YouTubeTranscriptApi

try:
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch('$VIDEO_ID')
    for entry in transcript.snippets:
        print(entry.text)
except Exception as e:
    import sys
    print(f'transcript-api failed: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null && exit 0

echo "Trying yt-dlp fallback..." >&2

# Method 2: yt-dlp subtitle extraction (fallback)
TMPDIR=$(mktemp -d)
yt-dlp --skip-download --write-auto-sub --sub-lang en --sub-format vtt \
  --output "$TMPDIR/%(id)s" "$URL" 2>/dev/null

# Parse VTT to plain text
VTT_FILE=$(find "$TMPDIR" -name "*.vtt" | head -1)
if [ -n "$VTT_FILE" ]; then
  # Strip VTT headers and timestamps, deduplicate lines
  sed '/^WEBVTT/d; /^$/d; /^[0-9][0-9]:/d; /^Kind:/d; /^Language:/d; /-->/d' "$VTT_FILE" \
    | awk '!seen[$0]++' 
  rm -rf "$TMPDIR"
  exit 0
fi

rm -rf "$TMPDIR"
echo "ERROR: No transcript/captions available for this video." >&2
exit 1
