#!/bin/bash
# Check American Airlines DEL->DFW flights for Feb 25, 2026

PRICE_FILE="/home/ubuntu/openclaw/memory/flight-price-history.json"
TARGET_PRICE=700

# Initialize file if it doesn't exist
if [ ! -f "$PRICE_FILE" ]; then
    echo '{"checks":[],"lowest_seen":99999}' > "$PRICE_FILE"
fi

echo "Checking AA flights DEL->DFW Feb 25..."
