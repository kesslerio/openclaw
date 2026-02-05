"""
Briefing Generator
Produces the final markdown briefing output
"""
from datetime import datetime
from typing import Dict, List

from .models import Briefing, MessageGroup, Classification, Platform, UnifiedMessage

class BriefingGenerator:
    def generate(self, briefing: Briefing) -> str:
        """Generate markdown briefing"""

        lines = [
            f"# 🧠 Universal Briefing",
            f"**Generated:** {briefing.generated_at.strftime('%Y-%m-%d %H:%M')}",
            f"**Window:** Last {briefing.time_window_hours} hours",
            f"**Processed:** {briefing.total_messages_processed} messages across {len(briefing.platforms_available)} platforms",
            "",
        ]

        # Platform status
        if briefing.platforms_failed:
            lines.append(f"⚠️ *Unavailable platforms: {', '.join(p.value for p in briefing.platforms_failed)}*")
            lines.append("")

        # URGENT section
        lines.append("---")
        lines.append("## 🚨 Urgent — Action Required")
        lines.append("")

        if briefing.urgent_groups:
            for group in sorted(briefing.urgent_groups, key=lambda g: -g.urgency_score):
                lines.extend(self._format_urgent_group(group))
        else:
            lines.append("*No urgent items requiring action.*")
        lines.append("")

        # FYI section
        lines.append("---")
        lines.append("## ℹ️ FYI — For Awareness")
        lines.append("")

        if briefing.fyi_groups:
            for group in briefing.fyi_groups:
                lines.extend(self._format_fyi_group(group))
        else:
            lines.append("*No informational updates.*")
        lines.append("")

        # NOISE section
        lines.append("---")
        lines.append("## 🔇 Noise — Filtered")
        lines.append("")
        lines.append(briefing.noise_summary or "*No noise filtered.*")
        lines.append("")

        # Commitments section
        if briefing.commitments_detected:
            lines.append("---")
            lines.append("## 📅 Commitments Detected")
            lines.append("")
            for msg in briefing.commitments_detected:
                deadline_str = msg.commitment_deadline.strftime('%a %m/%d %H:%M') if msg.commitment_deadline else "No deadline"
                who = "You committed" if msg.commitment_who == "me" else f"{msg.sender_name} committed"
                lines.append(f"- **{who}**: {msg.commitment_summary}")
                lines.append(f"  - ⏰ {deadline_str}")
                lines.append(f"  - Source: {msg.platform.value}")
            lines.append("")
            if briefing.calendar_events_created:
                lines.append(f"✅ *{briefing.calendar_events_created} calendar events created*")

        # Footer
        lines.append("")
        lines.append("---")
        lines.append(f"*Processing time: {briefing.processing_time_seconds:.1f}s*")

        return "\n".join(lines)

    def _format_urgent_group(self, group: MessageGroup) -> List[str]:
        """Format an urgent message group"""
        lines = []

        # Header
        platform_emoji = self._platform_emoji(group.platform)
        lines.append(f"### {platform_emoji} {group.topic}")
        lines.append(f"**From:** {group.primary_sender} | **Channel:** {group.channel_name or 'DM'}")
        lines.append("")

        # Summary
        lines.append(group.summary)
        lines.append("")

        # Individual urgent items with suggested replies
        for msg in group.messages:
            if msg.classification_confidence < 0.6:
                lines.append(f"⚠️ *Ambiguous — Review Recommended*")

            # Deadline if detected
            if msg.commitment_deadline:
                lines.append(f"⏰ **Deadline:** {msg.commitment_deadline.strftime('%a %m/%d %H:%M')}")

            # Suggested reply
            if msg.suggested_reply:
                lines.append("")
                lines.append("🔧 **Suggested Reply:**")
                lines.append(f"> {msg.suggested_reply}")

            lines.append("")

        return lines

    def _format_fyi_group(self, group: MessageGroup) -> List[str]:
        """Format an FYI message group"""
        lines = []

        platform_emoji = self._platform_emoji(group.platform)
        lines.append(f"### {platform_emoji} {group.topic}")
        lines.append("")
        lines.append(group.summary)
        lines.append("")

        # Key takeaways
        if len(group.messages) > 1:
            lines.append(f"*{len(group.messages)} related messages*")
            lines.append("")

        return lines

    def _platform_emoji(self, platform: Platform) -> str:
        """Get emoji for platform"""
        return {
            Platform.EMAIL: "📧",
            Platform.WHATSAPP: "💬",
            Platform.IMESSAGE: "📱",
            Platform.TELEGRAM: "✈️",
            Platform.SLACK: "💼",
            Platform.DISCORD: "🎮",
        }.get(platform, "💬")
