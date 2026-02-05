"""
CLI Interface
Provides /brief command
"""
import argparse
import sys

from .main import generate_briefing
from .integrations.followup_tracker import FollowUpTracker

def main():
    parser = argparse.ArgumentParser(
        description="Universal Briefing - Cross-platform message intelligence"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # /brief command
    brief_parser = subparsers.add_parser("brief", help="Generate briefing")
    brief_parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours to look back (default: 24)"
    )
    brief_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stdout)"
    )

    # /followups command
    followups_parser = subparsers.add_parser("followups", help="Show pending follow-ups")

    # /complete command
    complete_parser = subparsers.add_parser("complete", help="Mark follow-up complete")
    complete_parser.add_argument("id", type=int, help="Follow-up ID to complete")

    args = parser.parse_args()

    if args.command == "brief" or args.command is None:
        hours = getattr(args, 'hours', 24)
        output = generate_briefing(hours_back=hours)

        if hasattr(args, 'output') and args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Briefing saved to {args.output}")
        else:
            print(output)

    elif args.command == "followups":
        tracker = FollowUpTracker()
        followups = tracker.get_pending()

        if not followups:
            print("✅ No pending follow-ups!")
            return

        print("📋 Pending Follow-ups:\n")
        for f in followups:
            status_emoji = "🔴" if f.status == "overdue" else "🟡"
            deadline = f.deadline.strftime('%m/%d %H:%M') if f.deadline else "No deadline"
            print(f"{status_emoji} [{f.id}] {f.commitment}")
            print(f"   From: {f.sender} ({f.platform}) | Due: {deadline}")
            print()

    elif args.command == "complete":
        tracker = FollowUpTracker()
        tracker.mark_complete(args.id)
        print(f"✅ Follow-up {args.id} marked complete")

if __name__ == "__main__":
    main()
