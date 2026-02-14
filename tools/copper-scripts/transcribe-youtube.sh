#!/bin/bash
# Download YouTube audio and transcribe with Deepgram

VIDEO_URL="$1"
VIDEO_ID=$(echo "$VIDEO_URL" | grep -oP '(?<=v=)[^&]+' || echo "$VIDEO_URL" | grep -oP '(?<=youtu.be/)[^?]+')

if [ -z "$VIDEO_ID" ]; then
  echo "Could not extract video ID" >&2
  exit 1
fi

echo "Video ID: $VIDEO_ID" >&2

DEEPGRAM_KEY="d6f8670810ed8267b2564a925b4493c78811c6ed"
AUDIO_FILE="/tmp/yt_audio_${VIDEO_ID}.mp3"

# Try to download using youtube-dl with cookies from Playwright session
echo "Attempting download via Playwright..." >&2

# Create a simple Node script to download
cat > /tmp/download_audio.js << 'EOF'
const { chromium } = require('playwright');
const fs = require('fs');
const https = require('https');
const http = require('http');

async function downloadAudio(videoId) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto(`https://www.youtube.com/watch?v=${videoId}`, { waitUntil: 'networkidle', timeout: 60000 });
    
    // Extract audio stream URL from player response
    const audioUrl = await page.evaluate(() => {
      if (window.ytInitialPlayerResponse) {
        const formats = window.ytInitialPlayerResponse.streamingData?.adaptiveFormats || [];
        const audioFormat = formats.find(f => f.mimeType?.includes('audio/mp4') || f.mimeType?.includes('audio/webm'));
        return audioFormat?.url;
      }
      return null;
    });
    
    if (audioUrl) {
      console.log(audioUrl);
    } else {
      console.error('No audio URL found');
      process.exit(1);
    }
  } finally {
    await browser.close();
  }
}

downloadAudio(process.argv[2]);
EOF

cd /home/ubuntu/openclaw
AUDIO_URL=$(node /tmp/download_audio.js "$VIDEO_ID" 2>/dev/null)

if [ -z "$AUDIO_URL" ]; then
  echo "Could not get audio URL" >&2
  exit 1
fi

echo "Downloading audio..." >&2
curl -sL "$AUDIO_URL" -o "$AUDIO_FILE" --max-filesize 50000000

if [ ! -f "$AUDIO_FILE" ] || [ ! -s "$AUDIO_FILE" ]; then
  echo "Download failed" >&2
  exit 1
fi

echo "Transcribing with Deepgram..." >&2

# Send to Deepgram
curl -sX POST "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true" \
  -H "Authorization: Token $DEEPGRAM_KEY" \
  -H "Content-Type: audio/mp3" \
  --data-binary @"$AUDIO_FILE" \
  | jq -r '.results.channels[0].alternatives[0].transcript // empty'

rm -f "$AUDIO_FILE"
