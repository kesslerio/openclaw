"""
Journalist Configuration
Settings for auto journal generation
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
JOURNALS_DIR = DATA_DIR / "journals"
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Ensure directories exist
for dir_path in [JOURNALS_DIR, TEMPLATES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Claude (Anthropic) - enforced via model_enforcer
# No API key validation here - handled by ModelEnforcer

# Journal Generation
JOURNAL_MODEL = "claude-sonnet-4-20250514"  # Enforced by ModelEnforcer
JOURNAL_TEMPERATURE = 0.7  # Creative but coherent
JOURNAL_MAX_TOKENS = 3000  # Long enough for rich journals

# Diagram Settings
ENABLE_DIAGRAMS = True
DIAGRAM_TYPES = ["mindmap", "graph", "sequence"]  # Mermaid diagram types

# Automation
JOURNAL_TIME = "08:00"  # 8 AM CST - generate yesterday's journal
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "arvind@copperdigital.com")
NOTIFICATION_TELEGRAM = True

# Cost Settings
ESTIMATED_COST_PER_JOURNAL = 0.03  # $0.03 per journal (Claude Sonnet 4)
MONTHLY_BUDGET = 5.00  # $5/month for ~165 journals (on Max 200 plan)
