"""
Memex JOURNALIST - Auto Journal Generator
Generate daily journals from transcripts with AI
"""

__version__ = "1.0.0"

from .prompt_engineer import PromptEngineer
from .journal_generator import JournalGenerator
from .automation import DailyAutomation

__all__ = [
    "PromptEngineer",
    "JournalGenerator", 
    "DailyAutomation",
]
