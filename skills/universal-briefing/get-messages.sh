#!/bin/bash
# Quick message intelligence for OpenClaw briefings
# Returns just urgent/FYI messages in compact format

cd "$(dirname "$0")"
source venv/bin/activate

python3 << 'EOF'
from scripts.main import UniversalBriefing

briefing = UniversalBriefing()
briefing_obj = briefing.run(hours_back=24)

# Extract urgent groups
urgent = briefing_obj.urgent_groups
fyi = briefing_obj.fyi_groups

if not urgent and not fyi:
    print("📬 No urgent messages")
else:
    if urgent:
        print("📨 URGENT MESSAGES\n")
        for group in urgent[:3]:  # Top 3
            print(f"• {group.primary_sender}: {group.summary[:100]}...")

    if fyi and len(fyi) > 0:
        print(f"\nℹ️ {len(fyi)} FYI updates")

# Show commitment count
commits = briefing_obj.commitments_detected
if commits:
    print(f"📅 {len(commits)} commitment(s) detected")
EOF
