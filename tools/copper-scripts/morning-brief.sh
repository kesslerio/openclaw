#!/bin/bash
# Morning Brief Generator
# Comprehensive daily briefing for Arvind

echo "🌅 MORNING BRIEF - $(date '+%A, %B %d, %Y')"
echo "============================================="
echo ""

# 1. Weather
echo "☀️ WEATHER - Dallas, TX"
echo "------------------------"
WEATHER=$(curl -s "wttr.in/Dallas,TX?format=%C+%t+feels+like+%f,+%w+wind" 2>/dev/null)
echo "$WEATHER"
echo ""

# 2. Mission Control - To-Do
echo "📋 MISSION CONTROL"
echo "------------------"
echo "YOUR PRIORITIES TODAY:"
if [ -f /home/ubuntu/clawd/memory/arvind-todo-jan28.md ]; then
    grep -E "^\- \[ \]" /home/ubuntu/clawd/memory/arvind-todo-jan28.md | head -5 | sed 's/- \[ \]/  •/'
fi
echo ""

# 3. Nike's Work
echo "🐾 NIKE'S WORK"
echo "--------------"
echo "What I did overnight:"
if [ -f "/home/ubuntu/clawd/second-brain/journal/$(date '+%Y-%m-%d').md" ]; then
    grep -A3 "### Night" "/home/ubuntu/clawd/second-brain/journal/$(date '+%Y-%m-%d').md" 2>/dev/null | head -5
else
    echo "  • Building tools and automation"
fi
echo ""
echo "What I'm working on today:"
echo "  • Flight price monitoring"
echo "  • Email monitoring for important messages"
echo "  • Research for afternoon report"
echo ""

# 4. Flight Status
echo "✈️ FLIGHT STATUS"
echo "----------------"
if [ -f /home/ubuntu/clawd/memory/flight-tracking.json ]; then
    OUT=$(jq -r '.lowest_seen.outbound' /home/ubuntu/clawd/memory/flight-tracking.json)
    RET=$(jq -r '.lowest_seen.return' /home/ubuntu/clawd/memory/flight-tracking.json)
    echo "  DFW→DEL (~Feb 9): \$$OUT (target: <\$800)"
    echo "  DEL→DFW (Feb 25): \$$RET (target: <\$700)"
fi
echo ""

# 5. Email Highlights
echo "📧 EMAIL HIGHLIGHTS"
echo "-------------------"
IMPORTANT=$(himalaya envelope list -a work -f INBOX 2>/dev/null | grep -iE "Yugal|Vivin|Michael McGowan|Manas" | head -3)
if [ -n "$IMPORTANT" ]; then
    echo "$IMPORTANT"
else
    echo "  No critical emails from key contacts"
fi
echo ""

# 6. Quick Market Check (if markets open)
echo "📈 MARKETS (Yesterday's Close)"
echo "------------------------------"
echo "  Check after market open for updates"
echo ""

# 7. Proactive Ideas
echo "💡 PROACTIVE IDEAS FOR TODAY"
echo "----------------------------"
echo "  • Review Copper AI meeting prep (Feb 3 with Vivin)"
echo "  • Check progress on pamphlet to home health agencies"
echo "  • Consider content around upcoming Mac Studio arrival"
echo ""

echo "============================================="
echo "Have a great day! 🐾 -Nike"
echo "Generated at $(date '+%H:%M %Z')"
