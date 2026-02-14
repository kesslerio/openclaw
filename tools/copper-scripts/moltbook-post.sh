#!/bin/bash
# Moltbook Posting Script
# Post updates to the AI agent social network

set -euo pipefail

source ~/.moltbot/config/moltbook.env

SUBMOLT="${1:-general}"
TITLE="$2"
CONTENT="$3"

# Strip 'm/' prefix if present (common mistake)
SUBMOLT="${SUBMOLT#m/}"

if [ -z "$TITLE" ] || [ -z "$CONTENT" ]; then
    echo "Usage: moltbook-post.sh [submolt] \"title\" \"content\""
    echo ""
    echo "Example:"
    echo "  moltbook-post.sh general \"Working on email automation\" \"Just built an email management system...\""
    echo ""
    echo "Note: Use 'general' NOT 'm/general' for submolt parameter"
    exit 1
fi

echo "📝 Posting to submolt: $SUBMOLT..."
echo "Title: $TITLE"
echo ""

curl -X POST https://www.moltbook.com/api/v1/posts \
  -H "Authorization: Bearer $MOLTBOOK_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"submolt\": \"$SUBMOLT\",
    \"title\": \"$TITLE\",
    \"content\": \"$CONTENT\"
  }" | jq .

echo ""
echo "✅ Post submitted!"
echo "Profile: https://www.moltbook.com/u/SarinAI"
