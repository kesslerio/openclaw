"""
Abstract base class for all platform connectors
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta
from ..models import UnifiedMessage, Platform

class BaseConnector(ABC):
    """Base class all connectors must implement"""

    platform: Platform

    @abstractmethod
    def is_available(self) -> bool:
        """Check if connector is properly configured and accessible"""
        pass

    @abstractmethod
    def fetch_messages(
        self,
        hours_back: int = 24,
        channel_filter: Optional[str] = None
    ) -> List[UnifiedMessage]:
        """
        Fetch messages from the platform.
        Must return UnifiedMessage objects with all required fields populated.
        """
        pass

    @abstractmethod
    def get_user_identifiers(self) -> List[str]:
        """Return list of identifiers that represent the current user"""
        pass

    def is_own_message(self, message: UnifiedMessage) -> bool:
        """Check if message was sent by the user"""
        user_ids = self.get_user_identifiers()
        return (
            message.sender_id in user_ids or
            message.sender_name.lower() in [u.lower() for u in user_ids]
        )
