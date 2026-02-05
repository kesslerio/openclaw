"""
Commitment Detector
Extracts promises, deadlines, and action items from messages
"""
import json
import re
from typing import List, Optional
from datetime import datetime
import anthropic

try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False

from ..models import UnifiedMessage
from ..config import config

# High-signal commitment patterns
COMMITMENT_PATTERNS = [
    r"\bi['']?ll\b",
    r"\bi will\b",
    r"\blet me\b",
    r"\bi['']?m going to\b",
    r"\bwill do\b",
    r"\bget back to you\b",
    r"\bfollow up\b",
    r"\bsend you\b",
    r"\bby (tomorrow|monday|tuesday|wednesday|thursday|friday|end of day|eod|next week)\b",
    r"\b(tomorrow|tonight|this week|next week)\b.*\b(send|review|check|call|meet)\b",
]

COMMITMENT_PROMPT = """Extract any commitments, promises, or time-bound tasks from this message.

Message from {sender}:
"{content}"

Extract commitments in JSON format:
{{
    "has_commitment": true/false,
    "commitments": [
        {{
            "summary": "Brief description of commitment",
            "who": "sender" or "recipient",
            "deadline_text": "the time reference if any",
            "action_type": "review|send|call|meet|task|other"
        }}
    ]
}}

Rules:
- Only extract actual promises/commitments, not general statements
- "I'll send this tomorrow" = commitment
- "That sounds good" = NOT a commitment
- If no commitments found, return {{"has_commitment": false, "commitments": []}}

Return ONLY valid JSON."""

class CommitmentDetector:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY) if config.ANTHROPIC_API_KEY else None

    def detect_commitments(self, messages: List[UnifiedMessage]) -> List[UnifiedMessage]:
        """Detect commitments in messages"""

        for msg in messages:
            # Pre-filter
            if not self._has_commitment_signal(msg.content):
                msg.has_commitment = False
                continue

            try:
                self._extract_commitment(msg)
            except Exception as e:
                msg.has_commitment = False

        return messages

    def _has_commitment_signal(self, content: str) -> bool:
        """Quick regex check for commitment patterns"""
        content_lower = content.lower()
        return any(
            re.search(pattern, content_lower)
            for pattern in COMMITMENT_PATTERNS
        )

    def _extract_commitment(self, msg: UnifiedMessage):
        """Use LLM to extract commitment details"""

        if not self.client:
            msg.has_commitment = False
            return

        prompt = COMMITMENT_PROMPT.format(
            sender=msg.sender_name,
            content=msg.content[:1000]
        )

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            result = json.loads(response.content[0].text)

            if result.get("has_commitment") and result.get("commitments"):
                commitment = result["commitments"][0]

                msg.has_commitment = True
                msg.commitment_summary = commitment.get("summary")
                msg.commitment_who = commitment.get("who")

                # Parse deadline
                deadline_text = commitment.get("deadline_text")
                if deadline_text and DATEPARSER_AVAILABLE:
                    msg.commitment_deadline = dateparser.parse(
                        deadline_text,
                        settings={'PREFER_DATES_FROM': 'future'}
                    )
            else:
                msg.has_commitment = False

        except (json.JSONDecodeError, KeyError):
            msg.has_commitment = False
