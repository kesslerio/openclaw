#!/bin/bash
# prospect-research.sh
# Quick research tool for home health agency prospects
# Usage: ./prospect-research.sh "Agency Name" "City, State"

AGENCY_NAME="$1"
LOCATION="$2"

if [ -z "$AGENCY_NAME" ]; then
    echo "Usage: ./prospect-research.sh \"Agency Name\" \"City, State\""
    exit 1
fi

echo "🔍 Researching: $AGENCY_NAME"
echo "📍 Location: ${LOCATION:-Unknown}"
echo "---"

# Create research file
SAFE_NAME=$(echo "$AGENCY_NAME" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
DATE=$(date +%Y-%m-%d)
OUTPUT_FILE="prospects/${SAFE_NAME}-${DATE}.md"

mkdir -p prospects

cat > "$OUTPUT_FILE" << EOF
# Prospect Research: $AGENCY_NAME

**Date:** $DATE
**Location:** ${LOCATION:-TBD}
**Status:** 🔵 New Lead

## Basic Info
- **Agency Name:** $AGENCY_NAME
- **City/State:** ${LOCATION:-}
- **Website:** 
- **Phone:** 
- **Key Contact:** 

## Agency Profile
- **Estimated Size:** (caregivers)
- **Services:** 
- **Medicare Certified:** Yes/No
- **Medicaid Provider:** Yes/No

## Pain Points (to discover)
- [ ] EVV compliance challenges?
- [ ] After-hours call volume?
- [ ] No-show rate?
- [ ] Scheduling software used?
- [ ] Admin headcount?

## Research Notes


## Outreach Log
| Date | Action | Notes |
|------|--------|-------|
| $DATE | Research created | Initial prospect file |

---
*Created by Nike 🐾*
EOF

echo "✅ Created: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "1. Research their website"
echo "2. Find key contacts on LinkedIn"
echo "3. Check CMS/HHS databases for size"
echo "4. Add to outreach sequence"
