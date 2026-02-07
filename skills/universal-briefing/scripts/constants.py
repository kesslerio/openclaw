"""
Centralized constants for Universal Briefing.
Single source of truth for model IDs, retry settings, and DB settings.
"""

# Anthropic model to use for all LLM calls
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"

# Retry settings for API calls
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds
RETRY_MAX_DELAY = 30.0  # seconds

# Database settings
DB_TIMEOUT = 5.0  # seconds
DB_BUSY_TIMEOUT = 5000  # milliseconds

# Rate limiting
RATE_LIMIT_SENDS = 5
RATE_LIMIT_WINDOW = 60  # seconds

# Backup settings
MAX_BACKUPS = 7
