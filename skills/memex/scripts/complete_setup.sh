#!/bin/bash
#
# Memex Setup Completion Script
# Verifies all components and provides next steps
#

set -e

MEMEX_DIR="/Users/arvindsarin/Cursor/Claude-2026/openclaw/skills/memex"
cd "$MEMEX_DIR"

echo "🎯 Memex Setup Verification"
echo "============================"
echo ""

# Check .env file
echo "1. Checking environment configuration..."
if [[ -f "${MEMEX_DIR}/.env" ]]; then
    echo "   ✅ .env file exists"

    # Source .env
    set -a
    source "${MEMEX_DIR}/.env" 2>/dev/null || true
    set +a

    # Check if API key is set
    if [[ -n "$ANTHROPIC_API_KEY" ]] && [[ "$ANTHROPIC_API_KEY" != "sk-ant-api03-YOUR_KEY_HERE" ]]; then
        echo "   ✅ ANTHROPIC_API_KEY is configured"
        KEY_SET=true
    else
        echo "   ⚠️  ANTHROPIC_API_KEY not configured"
        echo "      Get your API key from: https://console.anthropic.com/settings/keys"
        echo "      Edit: ${MEMEX_DIR}/.env"
        KEY_SET=false
    fi
else
    echo "   ❌ .env file missing"
    KEY_SET=false
fi
echo ""

# Check cron jobs
echo "2. Checking cron jobs..."
if [[ -f ~/.openclaw/jobs.json ]]; then
    DAILY_INGEST=$(grep -c "memex-daily-ingest" ~/.openclaw/jobs.json || true)
    BUILD_JOURNAL=$(grep -c "memex-build-journal" ~/.openclaw/jobs.json || true)

    if [[ $DAILY_INGEST -gt 0 ]]; then
        echo "   ✅ Daily ingest job configured (7 AM)"
    else
        echo "   ❌ Daily ingest job missing"
    fi

    if [[ $BUILD_JOURNAL -gt 0 ]]; then
        echo "   ✅ Journal build job configured (9 PM)"
    else
        echo "   ❌ Journal build job missing"
    fi
else
    echo "   ❌ jobs.json file missing"
fi
echo ""

# Check LaunchAgent
echo "3. Checking LaunchAgent..."
if [[ -f ~/Library/LaunchAgents/com.memex.api.plist ]]; then
    echo "   ✅ LaunchAgent plist exists"

    if launchctl list | grep -q "com.memex.api"; then
        echo "   ✅ LaunchAgent is loaded"
    else
        echo "   ⚠️  LaunchAgent not loaded"
        echo "      Run: launchctl load ~/Library/LaunchAgents/com.memex.api.plist"
    fi
else
    echo "   ❌ LaunchAgent plist missing"
fi
echo ""

# Check scripts
echo "4. Checking scripts..."
SCRIPTS=(
    "journal_backfill.py"
    "daily_ingest.py"
)

for script in "${SCRIPTS[@]}"; do
    if [[ -x "${MEMEX_DIR}/scripts/${script}" ]]; then
        echo "   ✅ ${script}"
    else
        echo "   ❌ ${script} (not executable)"
    fi
done
echo ""

# Check Python dependencies
echo "5. Checking Python dependencies..."
DEPS=("anthropic" "pydantic-settings")
for dep in "${DEPS[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo "   ✅ ${dep}"
    else
        echo "   ❌ ${dep} (not installed)"
    fi
done
echo ""

# Test model enforcement
echo "6. Testing model enforcement..."
if python3 -c "import sys; sys.path.insert(0, '.'); from config.model_enforcer import ModelEnforcer; print(f'   ✅ {ModelEnforcer.DEFAULT_MODEL}')" 2>&1 | grep -q "claude"; then
    echo "   ✅ Model enforcement working"
else
    echo "   ❌ Model enforcement failed"
fi
echo ""

# Summary
echo "============================"
echo "📋 Setup Summary"
echo "============================"
echo ""

if [[ "$KEY_SET" == "true" ]]; then
    echo "✅ Ready to use!"
    echo ""
    echo "Next steps:"
    echo "1. Test journal backfill:"
    echo "   cd $MEMEX_DIR"
    echo "   ./scripts/journal_backfill.py --max 5"
    echo ""
    echo "2. Check API server:"
    echo "   curl http://localhost:8765/"
    echo ""
    echo "3. View logs:"
    echo "   tail -f ~/.openclaw/logs/memex-*.log"
else
    echo "⚠️  Setup incomplete!"
    echo ""
    echo "Required action:"
    echo "1. Get your Anthropic API key from:"
    echo "   https://console.anthropic.com/settings/keys"
    echo ""
    echo "2. Edit the .env file:"
    echo "   nano ${MEMEX_DIR}/.env"
    echo ""
    echo "3. Replace YOUR_KEY_HERE with your actual API key"
    echo ""
    echo "4. Restart this script to verify:"
    echo "   ./scripts/complete_setup.sh"
fi
echo ""
