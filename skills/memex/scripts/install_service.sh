#!/bin/bash
# Install Memex HISTORIAN API as a macOS LaunchAgent

PLIST_SOURCE="/Users/arvindsarin/Cursor/Claude-2026/openclaw/skills/memex/scripts/com.copperdigital.memex-api.plist"
PLIST_DEST="/Users/arvindsarin/Library/LaunchAgents/com.copperdigital.memex-api.plist"

echo "Installing Memex HISTORIAN Search API as a LaunchAgent..."

# Make scripts executable
chmod +x /Users/arvindsarin/Cursor/Claude-2026/openclaw/skills/memex/scripts/start_api.sh
chmod +x /Users/arvindsarin/Cursor/Claude-2026/openclaw/skills/memex/scripts/stop_api.sh
chmod +x /Users/arvindsarin/Cursor/Claude-2026/openclaw/skills/memex/scripts/status_api.sh

# Unload existing service if running
if launchctl list | grep -q com.copperdigital.memex-api; then
    echo "Unloading existing service..."
    launchctl unload "$PLIST_DEST" 2>/dev/null
fi

# Load the service
echo "Loading service..."
launchctl load "$PLIST_DEST"

# Check status
sleep 2
if launchctl list | grep -q com.copperdigital.memex-api; then
    echo ""
    echo "✓ Service installed and running!"
    echo ""
    echo "Commands:"
    echo "  Start:  launchctl start com.copperdigital.memex-api"
    echo "  Stop:   launchctl stop com.copperdigital.memex-api"
    echo "  Status: launchctl list | grep memex-api"
    echo ""
    echo "API available at: http://localhost:8765"
    echo "Logs: ~/Library/Logs/memex-api*.log"
else
    echo "✗ Service installation failed. Check logs at ~/Library/Logs/memex-api-error.log"
    exit 1
fi
