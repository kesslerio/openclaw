"""
Centralized configuration for Universal Briefing
All credentials loaded from environment variables and .env file
"""
import os
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import pytz

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

def _get_anthropic_key_from_openclaw() -> str:
    """Try to get Anthropic API key from OpenClaw credential provider"""
    try:
        result = subprocess.run(
            ["openclaw", "message", "send", "--dry-run", "test"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # This is a hacky way but we're checking if OpenClaw has Anthropic configured
        # The real key would be retrieved via OpenClaw's SDK if available
        return ""  # Will be set at runtime when OpenClaw invokes the skill
    except:
        return ""

@dataclass
class Config:
    # Time settings
    DEFAULT_HOURS_BACK: int = 24
    TIMEZONE: str = os.getenv("TZ", "America/Los_Angeles")

    # Database
    DB_PATH: Path = Path.home() / ".universal-briefing" / "briefing.db"

    # API Keys (from environment or OpenClaw)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", _get_anthropic_key_from_openclaw())

    # Gmail
    GMAIL_CREDENTIALS_PATH: Path = Path.home() / ".universal-briefing" / "gmail_credentials.json"
    GMAIL_TOKEN_PATH: Path = Path.home() / ".universal-briefing" / "gmail_token.pickle"

    # WhatsApp Business
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_USER_ID: int = int(os.getenv("TELEGRAM_USER_ID", "0"))

    # Slack
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_USER_ID: str = os.getenv("SLACK_USER_ID", "")

    # Discord
    DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
    DISCORD_USER_ID: int = int(os.getenv("DISCORD_USER_ID", "0"))

    # Google Calendar
    GCAL_CREDENTIALS_PATH: Path = Path.home() / ".universal-briefing" / "gcal_credentials.json"
    GCAL_TOKEN_PATH: Path = Path.home() / ".universal-briefing" / "gcal_token.pickle"

    # iMessage (macOS only)
    IMESSAGE_DB_PATH: Path = Path.home() / "Library" / "Messages" / "chat.db"

    # User identity (for filtering own messages)
    USER_EMAILS: list = None
    USER_PHONE_NUMBERS: list = None
    USER_NAMES: list = None

    def __post_init__(self):
        self.USER_EMAILS = [e.strip() for e in os.getenv("USER_EMAILS", "").split(",") if e.strip()]
        self.USER_PHONE_NUMBERS = [p.strip() for p in os.getenv("USER_PHONE_NUMBERS", "").split(",") if p.strip()]
        self.USER_NAMES = [n.strip() for n in os.getenv("USER_NAMES", "").split(",") if n.strip()]
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

config = Config()
