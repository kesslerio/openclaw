"""
Reply Generator
Generates context-aware draft replies matching platform norms
"""
import json
from typing import Optional, List
import anthropic

from ..models import UnifiedMessage, Platform
from ..config import config

# Platform-specific reply norms
PLATFORM_NORMS = {
    Platform.EMAIL: {
        "style": "Professional, complete sentences, proper greeting/sign-off",
        "length": "2-4 sentences, can be longer for complex topics",
        "example": "Hi [Name],\n\nThanks for reaching out. [Response]\n\nBest,\n[User]"
    },
    Platform.WHATSAPP: {
        "style": "Casual but clear, can use light emoji, no formal greeting needed",
        "length": "1-3 sentences, brief",
        "example": "Got it! Will [action] 👍"
    },
    Platform.IMESSAGE: {
        "style": "Very casual, conversational, emoji acceptable",
        "length": "1-2 sentences, very brief",
        "example": "On it! Will have that for you by [time]"
    },
    Platform.TELEGRAM: {
        "style": "Casual, can be brief, emoji acceptable",
        "length": "1-3 sentences",
        "example": "Sure, I'll [action]. Should be done by [time]."
    },
    Platform.SLACK: {
        "style": "Professional-casual, can use formatting, emoji acceptable",
        "length": "2-4 sentences, can use bullet points",
        "example": "Thanks for flagging this! I'll:\n• [Action 1]\n• [Action 2]\nETA: [time]"
    },
    Platform.DISCORD: {
        "style": "Casual, gaming-friendly, emoji common",
        "length": "1-3 sentences",
        "example": "Got it! Will handle that rn 👍"
    }
}

REPLY_PROMPT = """Generate a draft reply for this message.

Original Message:
- Platform: {platform}
- From: {sender}
- Context: {channel}
- Content: "{content}"
- Classification: {classification}
- Why reply needed: {reason}

Platform norms for {platform}:
- Style: {style}
- Length: {length}
- Example format: {example}

Generate a reply that:
1. Directly addresses the question/request
2. Matches the sender's tone
3. Is action-oriented and specific
4. Follows platform norms

Output JSON only:
{{
    "reply": "The draft reply text",
    "tone_match": "brief description of tone matching"
}}"""

class ReplyGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY) if config.ANTHROPIC_API_KEY else None

    def generate_replies(self, messages: List[UnifiedMessage]) -> List[UnifiedMessage]:
        """Generate draft replies for urgent messages"""

        from ..models import Classification

        for msg in messages:
            if msg.classification != Classification.URGENT:
                continue

            try:
                reply = self._generate_reply(msg)
                msg.suggested_reply = reply
            except Exception as e:
                msg.suggested_reply = None

        return messages

    def _generate_reply(self, msg: UnifiedMessage) -> Optional[str]:
        """Generate a single reply"""

        if not self.client:
            return None

        norms = PLATFORM_NORMS.get(msg.platform, PLATFORM_NORMS[Platform.EMAIL])

        prompt = REPLY_PROMPT.format(
            platform=msg.platform.value,
            sender=msg.sender_name,
            channel=msg.channel_name or "Direct Message",
            content=msg.content[:1000],
            classification=msg.classification.value,
            reason=msg.classification_reason,
            style=norms["style"],
            length=norms["length"],
            example=norms["example"]
        )

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            result = json.loads(response.content[0].text)
            return result.get("reply")
        except (json.JSONDecodeError, KeyError):
            return None
