"""
Memex Integrations Package

Data source integrations for Gmail, Calendar, and other services.
"""

from .gmail_service import GmailService, GmailConfig, GmailCredentials
from .calendar_service import CalendarService, CalendarConfig, CalendarCredentials
from .models import EmailData, CalendarEvent, IntegrationConfig

__all__ = [
    # Gmail
    "GmailService",
    "GmailConfig",
    "GmailCredentials",

    # Calendar
    "CalendarService",
    "CalendarConfig",
    "CalendarCredentials",

    # Models
    "EmailData",
    "CalendarEvent",
    "IntegrationConfig",
]

__version__ = "1.0.0"
