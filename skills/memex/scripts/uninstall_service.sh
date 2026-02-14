#!/bin/bash
# Uninstall Memex HISTORIAN API LaunchAgent

PLIST_DEST="/Users/arvindsarin/Library/LaunchAgents/com.copperdigital.memex-api.plist"

echo "Uninstalling Memex HISTORIAN Search API service..."

if launchctl list | grep -q com.copperdigital.memex-api; then
    echo "Stopping service..."
    launchctl unload "$PLIST_DEST"
    echo "✓ Service stopped and unloaded"
else
    echo "Service is not running"
fi

echo ""
echo "Service uninstalled. The plist file remains at:"
echo "$PLIST_DEST"
echo ""
echo "To reinstall, run: ./install_service.sh"
