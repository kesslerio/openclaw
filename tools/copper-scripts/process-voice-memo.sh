#!/bin/bash
# Voice Memo Processor
# Takes voice message file, transcribes it, creates task

set -euo pipefail

VOICE_FILE="$1"
TRANSCRIPT_DIR="$HOME/clawd/memory/voice-transcripts"
mkdir -p "$TRANSCRIPT_DIR"

if [ ! -f "$VOICE_FILE" ]; then
    echo "❌ Voice file not found: $VOICE_FILE"
    exit 1
fi

echo "🎙️ Processing voice memo: $(basename "$VOICE_FILE")"
echo ""

# Check if file is audio
file_type=$(file -b --mime-type "$VOICE_FILE")
if [[ ! "$file_type" =~ ^audio/ ]] && [[ ! "$file_type" =~ ^video/ ]]; then
    echo "❌ Not an audio/video file: $file_type"
    exit 1
fi

# Generate output filename
timestamp=$(date +%Y-%m-%d-%H%M%S)
transcript_file="$TRANSCRIPT_DIR/transcript-$timestamp.txt"

# Transcribe using whisper
echo "📝 Transcribing..."
if command -v whisper &> /dev/null; then
    whisper "$VOICE_FILE" --model base --output_format txt --output_dir "$TRANSCRIPT_DIR" --language en 2>&1 | grep -v "^Downloading"
    
    # Find the generated transcript
    latest_transcript=$(ls -t "$TRANSCRIPT_DIR"/*.txt 2>/dev/null | head -1)
    
    if [ -f "$latest_transcript" ]; then
        mv "$latest_transcript" "$transcript_file"
        echo ""
        echo "✅ Transcription complete!"
        echo ""
        echo "📄 Transcript:"
        echo "─────────────────────────────────────"
        cat "$transcript_file"
        echo "─────────────────────────────────────"
        echo ""
        echo "💾 Saved to: $transcript_file"
        echo ""
        echo "Next: Nike will analyze this and take action"
    else
        echo "❌ Transcription failed - no output file"
        exit 1
    fi
else
    echo "❌ whisper not installed"
    echo "Install: pip install openai-whisper"
    exit 1
fi
