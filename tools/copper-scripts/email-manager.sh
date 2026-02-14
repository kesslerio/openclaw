#!/bin/bash
# Email Management Script
# Checks unread emails, summarizes them, extracts todos

set -euo pipefail

WORK_ACCOUNT="work"
PERSONAL_ACCOUNT="personal"
SUMMARY_FILE="$HOME/Cursor/Claude-2026/openclaw/memory/email-summary-$(date +%Y-%m-%d).md"

echo "📧 Email Management - $(date)"
echo "================================"

# Function to get unread count
get_unread_count() {
    local account=$1
    himalaya -a "$account" envelope list --folder INBOX --query 'is:unseen' 2>/dev/null | wc -l || echo "0"
}

# Function to get unread emails
get_unread_emails() {
    local account=$1
    local limit=${2:-20}
    
    echo "## $account Account - $(date +%Y-%m-%d)" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
    
    # Get unread emails
    himalaya -a "$account" envelope list --folder INBOX --query 'is:unseen' --max-width 200 2>/dev/null | head -n $limit >> "$SUMMARY_FILE" || echo "No unread emails" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
}

# Check both accounts
work_unread=$(get_unread_count "$WORK_ACCOUNT" | tr -d '\n' | xargs)
personal_unread=$(get_unread_count "$PERSONAL_ACCOUNT" | tr -d '\n' | xargs)

echo "Work unread: $work_unread"
echo "Personal unread: $personal_unread"
echo ""

# Initialize summary file
echo "# Email Summary - $(date +%Y-%m-%d)" > "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "**Work:** $work_unread unread | **Personal:** $personal_unread unread" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# Get unread emails from both accounts
if [ "$work_unread" -gt 0 ]; then
    get_unread_emails "$WORK_ACCOUNT"
fi

if [ "$personal_unread" -gt 0 ]; then
    get_unread_emails "$PERSONAL_ACCOUNT"
fi

echo "✅ Email summary saved to: $SUMMARY_FILE"
echo ""
echo "Next: Nike will analyze this file and:"
echo "  1. Summarize important emails"
echo "  2. Extract todos → kanban"
echo "  3. Flag urgent items"
