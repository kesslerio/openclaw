#!/bin/bash
# Pilot Agency Tracker CLI
# Usage: ./pilot-tracker.sh [command] [args]
# Created: Feb 7, 2026 (Overnight Vibe Coding)

TRACKER_FILE="$(dirname "$0")/pilot-tracker.json"

show_help() {
    echo "🏥 ClearCare Pilot Agency Tracker"
    echo ""
    echo "Usage: ./pilot-tracker.sh [command]"
    echo ""
    echo "Commands:"
    echo "  status      Show pipeline summary"
    echo "  list        List all agencies"
    echo "  add         Add new agency (interactive)"
    echo "  update      Update agency stage"
    echo "  next        Show next actions due"
    echo "  help        Show this help"
    echo ""
}

show_status() {
    echo "📊 Pilot Recruitment Pipeline"
    echo "=============================="
    echo ""
    
    if command -v jq &> /dev/null; then
        target=$(jq -r '.meta.target_pilots' "$TRACKER_FILE")
        total=$(jq -r '.summary.total' "$TRACKER_FILE")
        active=$(jq -r '.summary.by_stage.pilot_active' "$TRACKER_FILE")
        
        echo "🎯 Target: $target pilots"
        echo "📋 Total leads: $total"
        echo "🚀 Active pilots: $active"
        echo ""
        echo "Pipeline:"
        jq -r '.summary.by_stage | to_entries[] | "  \(.key): \(.value)"' "$TRACKER_FILE"
    else
        echo "⚠️  Install jq for pretty output: brew install jq"
        cat "$TRACKER_FILE"
    fi
}

list_agencies() {
    echo "🏥 All Agencies"
    echo "==============="
    echo ""
    
    if command -v jq &> /dev/null; then
        jq -r '.agencies[] | "[\(.stage)] \(.name)\n    Contact: \(.contact)\n    Next: \(.next_action) (\(.next_action_date))\n"' "$TRACKER_FILE"
    else
        cat "$TRACKER_FILE"
    fi
}

show_next_actions() {
    echo "⚡ Next Actions Due"
    echo "==================="
    echo ""
    
    if command -v jq &> /dev/null; then
        today=$(date +%Y-%m-%d)
        jq -r --arg today "$today" '.agencies[] | select(.next_action_date <= $today) | "⏰ \(.name): \(.next_action)"' "$TRACKER_FILE"
        
        upcoming=$(jq -r '.agencies | sort_by(.next_action_date) | .[:5][] | "📅 \(.next_action_date): \(.name) - \(.next_action)"' "$TRACKER_FILE")
        
        if [ -n "$upcoming" ]; then
            echo ""
            echo "Coming up:"
            echo "$upcoming"
        fi
    else
        echo "⚠️  Install jq for this feature"
    fi
}

# Main
case "${1:-status}" in
    status)
        show_status
        ;;
    list)
        list_agencies
        ;;
    next)
        show_next_actions
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
