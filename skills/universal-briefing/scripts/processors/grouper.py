"""
Semantic Grouper
Groups related messages by topic, thread, and sender
"""
import json
from typing import List, Dict
from collections import defaultdict
import anthropic

from ..models import UnifiedMessage, MessageGroup, Classification, Platform
from ..config import config

GROUPING_PROMPT = """Group these messages by topic/theme.

Messages:
{messages}

Create topic clusters. Output JSON:
{{
    "groups": [
        {{
            "topic": "Short topic name",
            "message_ids": ["id1", "id2"],
            "summary": "One paragraph summary of this topic"
        }}
    ]
}}

Rules:
- Group by topic similarity, not just sender
- Collapse redundant messages
- Keep groups focused (2-10 messages ideal)
- Summary should capture key points

Return ONLY valid JSON."""

class SemanticGrouper:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY) if config.ANTHROPIC_API_KEY else None

    def group_messages(
        self,
        messages: List[UnifiedMessage]
    ) -> Dict[Classification, List[MessageGroup]]:
        """Group messages by classification and topic"""

        # First, group by classification
        by_classification = defaultdict(list)
        for msg in messages:
            by_classification[msg.classification].append(msg)

        result = {}

        for classification, msgs in by_classification.items():
            if classification == Classification.NOISE:
                # Just summarize noise, don't group
                result[classification] = [self._create_noise_summary(msgs)]
            elif len(msgs) <= 3:
                # Small groups don't need semantic grouping
                result[classification] = self._simple_groups(msgs)
            else:
                # Use LLM for larger groups
                result[classification] = self._semantic_group(msgs)

        return result

    def _simple_groups(self, messages: List[UnifiedMessage]) -> List[MessageGroup]:
        """Simple grouping by sender/channel"""
        groups = defaultdict(list)

        for msg in messages:
            key = f"{msg.platform.value}:{msg.channel_name or msg.sender_name}"
            groups[key].append(msg)

        return [
            MessageGroup(
                topic=f"{msgs[0].channel_name or msgs[0].sender_name}",
                messages=msgs,
                summary=self._quick_summary(msgs),
                primary_sender=msgs[0].sender_name,
                platform=msgs[0].platform,
                channel_name=msgs[0].channel_name,
                urgency_score=max(m.classification_confidence for m in msgs)
            )
            for msgs in groups.values()
        ]

    def _semantic_group(self, messages: List[UnifiedMessage]) -> List[MessageGroup]:
        """Use LLM to create semantic topic groups"""

        if not self.client:
            return self._simple_groups(messages)

        # Format messages for prompt
        msg_text = "\n".join([
            f"[{m.id}] {m.sender_name} ({m.platform.value}): {m.content[:200]}"
            for m in messages[:20]  # Limit for token efficiency
        ])

        prompt = GROUPING_PROMPT.format(messages=msg_text)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = json.loads(response.content[0].text)

            # Build message lookup
            msg_lookup = {m.id: m for m in messages}

            groups = []
            grouped_ids = set()

            for g in result.get("groups", []):
                group_msgs = [
                    msg_lookup[mid] for mid in g["message_ids"]
                    if mid in msg_lookup
                ]

                if not group_msgs:
                    continue

                grouped_ids.update(g["message_ids"])

                groups.append(MessageGroup(
                    topic=g["topic"],
                    messages=group_msgs,
                    summary=g["summary"],
                    primary_sender=group_msgs[0].sender_name,
                    platform=group_msgs[0].platform,
                    channel_name=group_msgs[0].channel_name,
                    urgency_score=max(m.classification_confidence for m in group_msgs)
                ))

            # Add ungrouped messages
            ungrouped = [m for m in messages if m.id not in grouped_ids]
            if ungrouped:
                groups.extend(self._simple_groups(ungrouped))

            return groups

        except (json.JSONDecodeError, KeyError):
            return self._simple_groups(messages)

    def _create_noise_summary(self, messages: List[UnifiedMessage]) -> MessageGroup:
        """Create summary group for noise messages"""

        platform_counts = defaultdict(int)
        for m in messages:
            platform_counts[m.platform.value] += 1

        summary = f"Filtered {len(messages)} low-signal messages: "
        summary += ", ".join(f"{count} from {plat}" for plat, count in platform_counts.items())

        return MessageGroup(
            topic="Filtered Noise",
            messages=[],  # Don't include actual messages
            summary=summary,
            primary_sender="Various",
            platform=Platform.EMAIL,  # Placeholder
            channel_name=None,
            urgency_score=0.0
        )

    def _quick_summary(self, messages: List[UnifiedMessage]) -> str:
        """Generate quick summary without LLM"""
        if len(messages) == 1:
            return messages[0].content[:200]

        return f"{len(messages)} messages from {messages[0].sender_name} about: {messages[0].content[:100]}..."
