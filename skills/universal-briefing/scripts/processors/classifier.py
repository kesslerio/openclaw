"""
Message Classifier
Classifies messages into Urgent, FYI, or Noise using LLM
"""
import json
from typing import List, Tuple

from ..models import UnifiedMessage, Classification
from ..config import config
from ..api_client import AnthropicClient
from ..constants import ANTHROPIC_MODEL
from ..logging_config import get_logger

logger = get_logger("classifier")

CLASSIFICATION_PROMPT = """Classify this message into exactly one category.

Message:
- Platform: {platform}
- Sender: {sender}
- Channel/Context: {channel}
- Content: "{content}"
- Has mention of me: {is_mention}
- Is direct message: {is_direct}

Categories:

🚨 URGENT - Needs action/reply:
- Direct questions to me
- Requests for decisions, approval, or action
- Deadlines or time-sensitive items
- Explicit mentions asking for response
- Blocking issues or dependencies

ℹ️ FYI - Informational:
- News, updates, announcements
- Status reports or progress updates
- Shared links or resources
- No explicit response required
- General information sharing

🔇 NOISE - Low value:
- Social chatter, jokes, memes
- Acknowledgments (ok, thanks, 👍)
- Reactions and emojis only
- Off-topic discussions
- Repetitive/low-signal content

Output JSON only:
{{
    "classification": "urgent" | "fyi" | "noise",
    "confidence": 0.0-1.0,
    "reason": "Brief explanation"
}}"""

class MessageClassifier:
    def __init__(self):
        self.client = AnthropicClient(api_key=config.ANTHROPIC_API_KEY)

    def classify_messages(
        self,
        messages: List[UnifiedMessage],
        batch_size: int = 10
    ) -> List[UnifiedMessage]:
        """Classify a list of messages"""

        for msg in messages:
            try:
                classification, confidence, reason = self._classify_single(msg)
                msg.classification = classification
                msg.classification_confidence = confidence
                msg.classification_reason = reason
            except Exception as e:
                logger.error("Classification error for %s: %s", msg.id, e)
                msg.classification = Classification.AMBIGUOUS
                msg.classification_confidence = 0.0
                msg.classification_reason = f"Classification error: {str(e)}"

        return messages

    def _classify_single(self, msg: UnifiedMessage) -> Tuple[Classification, float, str]:
        """Classify a single message"""

        # Quick heuristics for obvious cases
        quick_result = self._quick_classify(msg)
        if quick_result:
            return quick_result

        # Use LLM for complex cases
        if not self.client.available:
            return Classification.AMBIGUOUS, 0.5, "No API key configured"

        prompt = CLASSIFICATION_PROMPT.format(
            platform=msg.platform.value,
            sender=msg.sender_name,
            channel=msg.channel_name or "Direct Message",
            content=msg.content[:1000],  # Truncate
            is_mention=msg.is_mention,
            is_direct=msg.message_type.value == "direct"
        )

        response = self.client.create_message(
            model=ANTHROPIC_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            result = json.loads(response.content[0].text)
            classification = Classification(result["classification"])
            confidence = float(result["confidence"])
            reason = result["reason"]

            # Mark low confidence as ambiguous
            if confidence < 0.6:
                classification = Classification.AMBIGUOUS

            return classification, confidence, reason

        except (json.JSONDecodeError, KeyError, ValueError):
            return Classification.AMBIGUOUS, 0.0, "Parse error"

    def _quick_classify(self, msg: UnifiedMessage) -> Tuple[Classification, float, str] | None:
        """Quick heuristic classification for obvious cases"""
        content_lower = msg.content.lower().strip()

        # Obvious noise
        if len(content_lower) < 5:
            return Classification.NOISE, 0.95, "Very short message"

        if content_lower in ['ok', 'okay', 'k', 'thanks', 'thx', 'ty', '👍', '🙏', 'lol', 'haha']:
            return Classification.NOISE, 0.95, "Acknowledgment/reaction"

        # Strong urgent signals
        urgent_signals = [
            ('?' in content_lower and msg.is_mention, "Question with mention"),
            ('asap' in content_lower, "ASAP mentioned"),
            ('urgent' in content_lower, "Urgent keyword"),
            ('deadline' in content_lower, "Deadline mentioned"),
            ('need your' in content_lower, "Direct request"),
            ('can you' in content_lower and '?' in content_lower, "Direct question"),
            ('please respond' in content_lower, "Response requested"),
            ('waiting for' in content_lower, "Waiting indicator"),
        ]

        for condition, reason in urgent_signals:
            if condition:
                return Classification.URGENT, 0.85, reason

        # DMs are generally more urgent
        if msg.message_type.value == "direct" and '?' in content_lower:
            return Classification.URGENT, 0.8, "Direct question in DM"

        return None  # Use LLM for complex cases
