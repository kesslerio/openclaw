"""
CLI Interface
Provides /brief command
Signed-off-by: codex_nike
"""
import argparse
import sys

from .main import generate_briefing
from .integrations.followup_tracker import FollowUpTracker
from .listeners import run_listeners, status_report, run_api_server
from .connectors.email_connector import EmailConnector
from .connectors.slack_connector import SlackConnector
from .storage import MessageStore
from .models import Platform
from .logging_config import setup_logging, get_logger

logger = get_logger("cli")

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

    # /listen command
    listen_parser = subparsers.add_parser("listen", help="Run real-time listeners")
    listen_parser.add_argument("--whatsapp", action="store_true", help="Enable WhatsApp webhook listener")
    listen_parser.add_argument("--telegram", action="store_true", help="Enable Telegram polling listener")
    listen_parser.add_argument("--discord", action="store_true", help="Enable Discord gateway listener")
    listen_parser.add_argument("--all", action="store_true", help="Enable all listeners")
    listen_parser.add_argument("--host", type=str, default="0.0.0.0", help="Webhook host (WhatsApp)")
    listen_parser.add_argument("--port", type=int, default=8080, help="Webhook port (WhatsApp)")

    # /status command
    status_parser = subparsers.add_parser("status", help="Show listener/config status")
    status_parser.add_argument(
        "--hours",
        type=int,
        default=0,
        help="Hours to count stored messages (default: all time)",
    )

    # /api command
    api_parser = subparsers.add_parser("api", help="Run local inbox API")
    api_parser.add_argument("--host", type=str, default="127.0.0.1", help="API host")
    api_parser.add_argument("--port", type=int, default=8090, help="API port")
    api_parser.add_argument("--open-ui", action="store_true", help="Print UI URL")

    # /sync command
    sync_parser = subparsers.add_parser("sync", help="Fetch live email/slack and store")
    sync_parser.add_argument("--email", action="store_true", help="Sync email")
    sync_parser.add_argument("--slack", action="store_true", help="Sync Slack")
    sync_parser.add_argument("--hours", type=int, default=24, help="Hours back (default: 24)")

    # /backup command
    backup_parser = subparsers.add_parser("backup", help="Backup the message database")

    args = parser.parse_args()

    # Initialize logging for all commands
    setup_logging()

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

    elif args.command == "listen":
        import os

        # Safety gate: print clear status of auto-reply on startup
        auto_reply = os.getenv("UNIVERSAL_BRIEFING_AUTO_REPLY", "0")
        own_numbers = os.getenv("USER_PHONE_NUMBERS", "")
        webhook_secret = os.getenv("WEBHOOK_SECRET", "")

        print("=" * 60)
        print("UNIVERSAL BRIEFING LISTENER - SAFETY CHECK")
        print("=" * 60)

        if auto_reply == "1":
            if not own_numbers:
                print("ABORT: AUTO_REPLY is ON but USER_PHONE_NUMBERS is empty.")
                print("  Own-message detection will fail. Set USER_PHONE_NUMBERS first.")
                sys.exit(1)
            print(f"  AUTO-REPLY:       ON (messages to @c.us DMs only)")
            print(f"  OWN NUMBERS:      {own_numbers}")
        else:
            print(f"  AUTO-REPLY:       OFF (ingest only, no replies)")

        if webhook_secret:
            print(f"  WEBHOOK AUTH:     HMAC-SHA256 enabled")
        else:
            print(f"  WEBHOOK AUTH:     DISABLED (any POST accepted)")

        print(f"  BLOCKED TARGETS:  status@broadcast, @g.us groups, @lid")
        print(f"  RATE LIMIT:       5 sends / 60s per chatId")
        print(f"  PID:              {os.getpid()}")
        print("=" * 60)

        run_listeners(
            whatsapp=args.whatsapp,
            telegram=args.telegram,
            discord=args.discord,
            all_listeners=args.all,
            host=args.host,
            port=args.port,
        )
    elif args.command == "status":
        hours = args.hours if args.hours and args.hours > 0 else None
        status_report(hours_back=hours)
    elif args.command == "api":
        if args.open_ui:
            print(f"UI: http://{args.host}:{args.port}/ui")
        run_api_server(host=args.host, port=args.port)
    elif args.command == "sync":
        store = MessageStore()
        hours = args.hours if args.hours and args.hours > 0 else 24
        if not args.email and not args.slack:
            args.email = True
            args.slack = True
        if args.email:
            email = EmailConnector()
            if email.is_available():
                messages = email.fetch_messages(hours_back=hours)
                store.save_messages(messages)
                print(f"✅ Synced email: {len(messages)} messages")
            else:
                print("❌ Email connector unavailable")
        if args.slack:
            slack = SlackConnector()
            if slack.is_available():
                messages = slack.fetch_messages(hours_back=hours)
                store.save_messages(messages)
                print(f"✅ Synced Slack: {len(messages)} messages")
            else:
                print("❌ Slack connector unavailable")
    elif args.command == "backup":
        store = MessageStore()
        dest = store.backup()
        print(f"✅ Database backed up to {dest}")

if __name__ == "__main__":
    main()
