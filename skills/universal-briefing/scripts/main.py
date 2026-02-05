"""
Main Orchestrator
Runs the complete briefing pipeline
"""
import time
from datetime import datetime
from typing import List, Dict

from .config import config
from .models import UnifiedMessage, Briefing, Classification, Platform, MessageGroup

# Connectors
from .connectors.email_connector import EmailConnector
from .connectors.imessage_connector import iMessageConnector
from .connectors.whatsapp_connector import WhatsAppConnector
from .connectors.telegram_connector import TelegramConnector
from .connectors.slack_connector import SlackConnector
from .connectors.discord_connector import DiscordConnector

# Processors
from .processors.filter_engine import FilterEngine
from .processors.classifier import MessageClassifier
from .processors.commitment_detector import CommitmentDetector
from .processors.reply_generator import ReplyGenerator
from .processors.grouper import SemanticGrouper

# Integrations
from .integrations.calendar_sync import CalendarSync
from .integrations.followup_tracker import FollowUpTracker

# Output
from .briefing_generator import BriefingGenerator

class UniversalBriefing:
    def __init__(self):
        # Initialize connectors
        self.connectors = {
            Platform.EMAIL: EmailConnector(),
            Platform.IMESSAGE: iMessageConnector(),
            Platform.WHATSAPP: WhatsAppConnector(),
            Platform.TELEGRAM: TelegramConnector(),
            Platform.SLACK: SlackConnector(),
            Platform.DISCORD: DiscordConnector(),
        }

        # Collect user identifiers from all connectors
        user_ids = []
        for connector in self.connectors.values():
            user_ids.extend(connector.get_user_identifiers())
        user_ids.extend(config.USER_NAMES)

        # Initialize processors
        self.filter_engine = FilterEngine(user_ids)
        self.classifier = MessageClassifier()
        self.commitment_detector = CommitmentDetector()
        self.reply_generator = ReplyGenerator()
        self.grouper = SemanticGrouper()

        # Initialize integrations
        self.calendar = CalendarSync()
        self.tracker = FollowUpTracker()

        # Output generator
        self.briefing_gen = BriefingGenerator()

    def run(self, hours_back: int = 24) -> str:
        """Execute full briefing pipeline"""
        start_time = time.time()

        # 1. Fetch messages from all platforms
        all_messages = []
        platforms_available = []
        platforms_failed = []
        messages_by_platform = {}

        for platform, connector in self.connectors.items():
            if connector.is_available():
                try:
                    messages = connector.fetch_messages(hours_back=hours_back)
                    all_messages.extend(messages)
                    platforms_available.append(platform)
                    messages_by_platform[platform.value] = len(messages)
                except Exception as e:
                    platforms_failed.append(platform)
            else:
                platforms_failed.append(platform)

        total_raw = len(all_messages)

        # 2. Filter messages (remove system, bots, own, duplicates)
        filtered_messages = self.filter_engine.filter_messages(all_messages)

        # 3. Classify messages
        classified_messages = self.classifier.classify_messages(filtered_messages)

        # 4. Detect commitments
        messages_with_commitments = self.commitment_detector.detect_commitments(classified_messages)

        # 5. Generate replies for urgent messages
        messages_with_replies = self.reply_generator.generate_replies(messages_with_commitments)

        # 6. Group messages semantically
        grouped: Dict[Classification, List[MessageGroup]] = self.grouper.group_messages(messages_with_replies)

        # 7. Create calendar events for commitments
        commitments = [m for m in messages_with_replies if m.has_commitment]
        calendar_events_created = self.calendar.create_commitment_events(commitments)

        # 8. Track commitments
        for msg in commitments:
            self.tracker.add_followup(
                platform=msg.platform.value,
                sender=msg.sender_name,
                commitment=msg.commitment_summary or "",
                deadline=msg.commitment_deadline,
                source_message_id=msg.id
            )

        # 9. Build briefing object
        noise_groups = grouped.get(Classification.NOISE, [])
        noise_summary = noise_groups[0].summary if noise_groups else ""

        briefing = Briefing(
            generated_at=datetime.now(),
            time_window_hours=hours_back,
            urgent_groups=grouped.get(Classification.URGENT, []) + grouped.get(Classification.AMBIGUOUS, []),
            fyi_groups=grouped.get(Classification.FYI, []),
            noise_summary=noise_summary,
            total_messages_processed=total_raw,
            messages_by_platform=messages_by_platform,
            commitments_detected=commitments,
            calendar_events_created=calendar_events_created,
            platforms_available=platforms_available,
            platforms_failed=platforms_failed,
            processing_time_seconds=time.time() - start_time
        )

        # 10. Generate output
        return self.briefing_gen.generate(briefing)

def generate_briefing(hours_back: int = 24) -> str:
    """Main entry point"""
    briefing = UniversalBriefing()
    return briefing.run(hours_back=hours_back)
