#!/bin/bash
# Flight Price Monitor - DEL↔DFW
# Checks prices daily and alerts when below threshold

set -euo pipefail

REPORT_FILE="$HOME/clawd/memory/flight-prices-$(date +%Y-%m-%d).md"
THRESHOLD=750

echo "✈️ Flight Price Monitor - $(date)" | tee "$REPORT_FILE"
echo "================================" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Route details
echo "**Route:** Delhi (DEL) → Dallas (DFW)" | tee -a "$REPORT_FILE"
echo "**Outbound:** ~Feb 9, 2026 (±3 days) - 1 ticket" | tee -a "$REPORT_FILE"
echo "**Return:** Feb 25, 2026 - 3 tickets" | tee -a "$REPORT_FILE"
echo "**Airline:** American Airlines (one stop preferred)" | tee -a "$REPORT_FILE"
echo "**Alert Threshold:** Below \$${THRESHOLD}" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Note: Actual price checking would require:
# - Google Flights API (not publicly available)
# - Browser automation (Playwright/Puppeteer)
# - Or paid flight API (Skyscanner, Kiwi.com, etc.)

# For now, manual check with web_search
echo "**Status:** Manual check required (Google Flights doesn't have public API)" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"
echo "**Next Steps:**" | tee -a "$REPORT_FILE"
echo "1. Nike will check Google Flights via browser during morning heartbeat" | tee -a "$REPORT_FILE"
echo "2. Alert Arvind on Telegram + WhatsApp if prices drop below \$${THRESHOLD}" | tee -a "$REPORT_FILE"
echo "3. Daily monitoring continues until flights booked" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# URLs to check
echo "**Links to Monitor:**" | tee -a "$REPORT_FILE"
echo "- Outbound (Feb 6-12): https://www.google.com/travel/flights?q=flights%20from%20delhi%20to%20dallas%20february%202026" | tee -a "$REPORT_FILE"
echo "- Return (Feb 25): https://www.google.com/travel/flights?q=flights%20from%20dallas%20to%20delhi%20february%2025%202026" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "✅ Flight report saved to: $REPORT_FILE"
