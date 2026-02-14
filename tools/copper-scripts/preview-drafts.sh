#!/bin/bash
# Preview drafts folder via simple HTTP server
# Usage: ./preview-drafts.sh [port]

PORT=${1:-8080}
DRAFTS_DIR="/home/ubuntu/openclaw/drafts"

echo "🌐 Starting preview server..."
echo ""
echo "📄 Available files:"
ls -1 "$DRAFTS_DIR"/*.html 2>/dev/null | while read f; do
    basename "$f"
done
echo ""
echo "🔗 Open in browser:"
echo "   http://localhost:$PORT/icare-landing-page.html"
echo "   http://localhost:$PORT/icare-one-pager.html"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$DRAFTS_DIR"
python3 -m http.server $PORT
