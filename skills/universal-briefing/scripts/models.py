"""
Shared data models for Universal Briefing
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Platform(Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    IMESSAGE = "imessage"
    TELEGRAM = "telegram"
    SLACK = "slack"
    DISCORD = "discord"

class Classification(Enum):
    URGENT = "urgent"           # 🚨 Needs reply
    FYI = "fyi"                 # ℹ️ Informational
    NOISE = "noise"             # 🔇 Low signal
    AMBIGUOUS = "ambiguous"     # ⚠️ Review recommended

class MessageType(Enum):
    DIRECT = "direct"
    GROUP = "group"
    CHANNEL = "channel"

@dataclass
class UnifiedMessage:
    """Platform-agnostic message representation"""
    id: str
    platform: Platform
    sender_id: str
    sender_name: str
    content: str
    timestamp: datetime

    # Context
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
    message_type: MessageType = MessageType.DIRECT
    thread_id: Optional[str] = None
    reply_to_id: Optional[str] = None

    # Metadata
    is_mention: bool = False
    has_attachment: bool = False
    attachment_type: Optional[str] = None
    raw_data: dict = field(default_factory=dict)

    # Processing results (filled later)
    classification: Optional[Classification] = None
    classification_confidence: float = 0.0
    classification_reason: str = ""
    topic_cluster: Optional[str] = None

    # Commitment detection
    has_commitment: bool = False
    commitment_summary: Optional[str] = None
    commitment_deadline: Optional[datetime] = None
    commitment_who: Optional[str] = None  # "me" or sender

    # Generated content
    suggested_reply: Optional[str] = None

@dataclass
class MessageGroup:
    """Semantically grouped messages"""
    topic: str
    messages: List[UnifiedMessage]
    summary: str
    primary_sender: str
    platform: Platform
    channel_name: Optional[str]
    urgency_score: float = 0.0

@dataclass
class Briefing:
    """Complete briefing output"""
    generated_at: datetime
    time_window_hours: int

    urgent_groups: List[MessageGroup]
    fyi_groups: List[MessageGroup]
    noise_summary: str

    total_messages_processed: int
    messages_by_platform: dict

    commitments_detected: List[UnifiedMessage]
    calendar_events_created: int

    # Metadata
    platforms_available: List[Platform]
    platforms_failed: List[Platform]
    processing_time_seconds: float
