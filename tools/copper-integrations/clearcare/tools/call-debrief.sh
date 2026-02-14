#!/bin/bash
# Call Debrief Tool - Quick post-call capture
# Usage: ./call-debrief.sh [agency-id]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACKER_FILE="$SCRIPT_DIR/pilot-tracker.json"
MEMORY_DIR="/Users/arvindsarin/Cursor/Claude-2026/openclaw/memory"

echo "📞 CALL DEBRIEF TOOL"
echo "===================="
echo ""

# Get agency name
if [ -n "$1" ]; then
    AGENCY_ID=$1
else
    read -p "Agency/Contact Name: " AGENCY_NAME
fi

# Capture call details
echo ""
echo "--- Call Details ---"
read -p "Agency Name (if different): " FULL_AGENCY_NAME
read -p "Contact Name: " CONTACT_NAME
read -p "Their Role: " CONTACT_ROLE
read -p "Visits per month: " VISITS
read -p "Current no-show rate (%): " NOSHOW_RATE
read -p "EMR System: " EMR

echo ""
echo "--- Pain Points (comma-separated) ---"
read -p "Pain points: " PAIN_POINTS

echo ""
echo "--- Outcome ---"
echo "1) Interested - Ready for pilot"
echo "2) Interested - Needs internal buy-in"
echo "3) Maybe later"
echo "4) Not a fit"
read -p "Select outcome (1-4): " OUTCOME

case $OUTCOME in
    1) STAGE="pilot_active"; NEXT_ACTION="Send pilot setup email";;
    2) STAGE="demo"; NEXT_ACTION="Follow up with decision maker info";;
    3) STAGE="responded"; NEXT_ACTION="Nurture - check back in 30 days";;
    4) STAGE="lost"; NEXT_ACTION="None";;
    *) STAGE="discovery"; NEXT_ACTION="Review notes";;
esac

read -p "Next follow-up date (YYYY-MM-DD): " FOLLOWUP_DATE
read -p "Additional notes: " NOTES

# Generate debrief file
TODAY=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
DEBRIEF_FILE="$MEMORY_DIR/call-debrief-$TODAY-$TIME.md"

cat > "$DEBRIEF_FILE" << EOF
# Call Debrief: $CONTACT_NAME
**Date:** $TODAY $TIME

## Agency Details
- **Agency:** $FULL_AGENCY_NAME
- **Contact:** $CONTACT_NAME
- **Role:** $CONTACT_ROLE

## Key Metrics
- **Visits/month:** $VISITS
- **No-show rate:** $NOSHOW_RATE%
- **EMR System:** $EMR

## Pain Points
$PAIN_POINTS

## Outcome
- **Stage:** $STAGE
- **Next Action:** $NEXT_ACTION
- **Follow-up Date:** $FOLLOWUP_DATE

## Notes
$NOTES

---
*Captured via call-debrief.sh*
EOF

echo ""
echo "✅ Debrief saved to: $DEBRIEF_FILE"
echo ""
echo "--- Summary ---"
echo "Contact: $CONTACT_NAME at $FULL_AGENCY_NAME"
echo "Stage: $STAGE"
echo "Next: $NEXT_ACTION"
echo "Follow-up: $FOLLOWUP_DATE"
echo ""
echo "📧 Suggested email template: templates/post-discovery-email.md"
echo "📊 Update pilot tracker with: ./pilot-tracker.sh update [id]"
