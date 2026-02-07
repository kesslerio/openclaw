"""
Message Filter Engine
Applies exclusion rules to remove system messages, bots, duplicates, and own messages
"""
import hashlib
import re
from typing import List, Set
from ..models import UnifiedMessage, Platform

# System message patterns by platform
SYSTEM_PATTERNS = {
    Platform.EMAIL: [
        r"^(Delivery Status Notification|Mail Delivery Subsystem)",
        r"^(noreply|no-reply|donotreply)@",
        r"^mailer-daemon@",
        r"(unsubscribe|opt.out|manage.preferences)",
    ],
    Platform.WHATSAPP: [
        r"(joined using|left the group|changed the subject|changed this group's icon)",
        r"(Messages.*are end-to-end encrypted)",
        r"(created group|added you)",
        r"^(\u200e|\u200f)",  # RTL/LTR marks (system messages)
    ],
    Platform.IMESSAGE: [
        r'(liked|loved|disliked|laughed at|emphasized|questioned) ["\']',
        r"(is typing|read receipt|delivered)",
        r"(started a FaceTime|ended the call)",
    ],
    Platform.TELEGRAM: [
        r"(joined the group|left the group|pinned a message)",
        r"(changed the group|created the group)",
        r"^/\w+",  # Bot commands
    ],
    Platform.SLACK: [
        r"(has joined the channel|has left the channel)",
        r"(set the channel|channel was archived)",
        r"(uploaded a file|shared a file)",
        r"^/\w+",  # Slash commands
    ],
    Platform.DISCORD: [
        r"(joined the server|left the server)",
        r"(boosted the server|started a thread)",
        r"(pinned a message|started a call)",
    ],
}

# Bot indicators
BOT_PATTERNS = [
    r"\[BOT\]",
    r"(bot|automat|system|notification)$",
    r"^(github|gitlab|jira|confluence|notion|zapier|ifttt|slack)",
]

# Low-value message patterns
NOISE_PATTERNS = [
    r"^(ok|okay|k|kk|yes|no|yeah|yep|nope|sure|thanks|thx|ty|np|lol|haha|😂|👍|🙏|❤️|👀)+$",
    r"^\.+$",
    r"^\s*$",
]

class FilterEngine:
    def __init__(self, user_identifiers: List[str]):
        self.user_ids = set(id.lower() for id in user_identifiers if id)
        self._seen_content_hashes: Set[str] = set()

    def filter_messages(self, messages: List[UnifiedMessage]) -> List[UnifiedMessage]:
        """Apply all filters and return cleaned message list"""
        filtered = []

        for msg in messages:
            if self._should_exclude(msg):
                continue

            # Check for duplicates
            content_hash = self._content_hash(msg)
            if content_hash in self._seen_content_hashes:
                continue
            self._seen_content_hashes.add(content_hash)

            filtered.append(msg)

        return filtered

    def _should_exclude(self, msg: UnifiedMessage) -> bool:
        """Check if message should be excluded"""
        # Own message check
        if self._is_own_message(msg):
            return True

        # Empty content
        if not msg.content or not msg.content.strip():
            return True

        # System message check
        if self._is_system_message(msg):
            return True

        # Bot check
        if self._is_bot_message(msg):
            return True

        return False

    def _is_own_message(self, msg: UnifiedMessage) -> bool:
        """Check if message is from the user"""
        sender_lower = msg.sender_id.lower()
        return (
            sender_lower in self.user_ids or
            msg.sender_name.lower() in self.user_ids
        )

    def _is_system_message(self, msg: UnifiedMessage) -> bool:
        """Check if message is a system message"""
        patterns = SYSTEM_PATTERNS.get(msg.platform, [])
        content = msg.content.lower()
        sender = msg.sender_name.lower()

        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
            if re.search(pattern, sender, re.IGNORECASE):
                return True

        return False

    def _is_bot_message(self, msg: UnifiedMessage) -> bool:
        """Check if message is from a bot"""
        sender = msg.sender_name.lower()

        for pattern in BOT_PATTERNS:
            if re.search(pattern, sender, re.IGNORECASE):
                return True

        # Check raw data for bot flags
        if msg.raw_data.get("bot") or msg.raw_data.get("is_bot"):
            return True

        return False

    def _content_hash(self, msg: UnifiedMessage) -> str:
        """Generate deterministic hash for deduplication (survives process restarts)."""
        normalized = re.sub(r'\s+', ' ', msg.content.lower().strip())
        time_bucket = msg.timestamp.strftime("%Y%m%d%H")  # Hour bucket
        raw = f"{msg.sender_id}:{time_bucket}:{normalized}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def is_noise_only(self, content: str) -> bool:
        """Check if content is pure noise (reactions, acknowledgments)"""
        for pattern in NOISE_PATTERNS:
            if re.match(pattern, content.strip(), re.IGNORECASE):
                return True
        return False
