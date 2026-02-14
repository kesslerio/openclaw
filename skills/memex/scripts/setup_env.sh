#!/bin/bash
#
# Setup script for Memex Gmail/Calendar integration environment variables
#
# This script helps you securely set up environment variables for the Memex integration.
# It extracts credentials from credentials.json and sets them as environment variables.
#

set -e

CREDENTIALS_FILE="$HOME/clawd/credentials.json"
SHELL_RC=""

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    echo "⚠️  Unknown shell. Please manually add environment variables to your shell config."
    exit 1
fi

echo "🔧 Memex Environment Setup"
echo "=========================="
echo ""

# Check if credentials.json exists
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "❌ credentials.json not found at $CREDENTIALS_FILE"
    echo ""
    echo "Please download your OAuth credentials from Google Cloud Console:"
    echo "  1. Go to https://console.cloud.google.com/apis/credentials"
    echo "  2. Select project: memex-integrations"
    echo "  3. Download OAuth 2.0 Client ID credentials"
    echo "  4. Save as $CREDENTIALS_FILE"
    exit 1
fi

# Extract values from credentials.json
echo "📖 Reading credentials from $CREDENTIALS_FILE..."
CLIENT_ID=$(cat "$CREDENTIALS_FILE" | grep -o '"client_id": *"[^"]*"' | head -1 | sed 's/.*: *"\(.*\)"/\1/')
CLIENT_SECRET=$(cat "$CREDENTIALS_FILE" | grep -o '"client_secret": *"[^"]*"' | head -1 | sed 's/.*: *"\(.*\)"/\1/')
PROJECT_ID=$(cat "$CREDENTIALS_FILE" | grep -o '"project_id": *"[^"]*"' | head -1 | sed 's/.*: *"\(.*\)"/\1/')

if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ] || [ -z "$PROJECT_ID" ]; then
    echo "❌ Failed to extract credentials from JSON file"
    exit 1
fi

echo "✅ Extracted credentials successfully"
echo ""

# Check if already set
if grep -q "GOOGLE_CLIENT_ID" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  Environment variables already exist in $SHELL_RC"
    read -p "Do you want to update them? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping update."
        exit 0
    fi

    # Remove old entries
    echo "🗑️  Removing old entries..."
    sed -i.bak '/^export GOOGLE_CLIENT_ID=/d' "$SHELL_RC"
    sed -i.bak '/^export GOOGLE_CLIENT_SECRET=/d' "$SHELL_RC"
    sed -i.bak '/^export GOOGLE_PROJECT_ID=/d' "$SHELL_RC"
    sed -i.bak '/^export MEMEX_ENCRYPTION_KEY=/d' "$SHELL_RC"
fi

# Generate encryption key
ENCRYPTION_KEY=$(openssl rand -base64 32)

# Add to shell config
echo "" >> "$SHELL_RC"
echo "# Memex Gmail/Calendar Integration - Added $(date)" >> "$SHELL_RC"
echo "export GOOGLE_CLIENT_ID=\"$CLIENT_ID\"" >> "$SHELL_RC"
echo "export GOOGLE_CLIENT_SECRET=\"$CLIENT_SECRET\"" >> "$SHELL_RC"
echo "export GOOGLE_PROJECT_ID=\"$PROJECT_ID\"" >> "$SHELL_RC"
echo "export MEMEX_ENCRYPTION_KEY=\"$ENCRYPTION_KEY\"" >> "$SHELL_RC"

echo "✅ Added environment variables to $SHELL_RC"
echo ""
echo "🔒 Security notes:"
echo "  - Credentials are now in environment variables (more secure)"
echo "  - Token encryption key generated"
echo "  - credentials.json will be removed from git tracking"
echo ""
echo "⚡ Next steps:"
echo "  1. Source your shell config: source $SHELL_RC"
echo "  2. Verify: echo \$GOOGLE_PROJECT_ID"
echo "  3. Optionally delete $CREDENTIALS_FILE (credentials are now in env)"
echo ""
echo "🔄 Restart your shell or run: source $SHELL_RC"
