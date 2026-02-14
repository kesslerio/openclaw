#!/usr/bin/env python3
"""
Daily Journal Generator Script
Run this script daily (via cron) to auto-generate journals
"""

import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from journalist import DailyAutomation

# Use MEMEX_BASE env var or fallback to script location
MEMEX_BASE = Path(os.getenv("MEMEX_BASE", Path(__file__).resolve().parents[1]))
LOG_FILE = MEMEX_BASE / "logs" / "journalist.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(LOG_FILE)),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    logger.info("=== Daily Journal Generation Started ===")
    
    try:
        automation = DailyAutomation()
        journal_data = automation.generate_daily_journal()
        
        if journal_data:
            logger.info(f"✅ Journal generated successfully for {journal_data['date']}")
            logger.info(f"   Transcripts: {journal_data['transcript_count']}")
            logger.info(f"   Action items: {len(journal_data['action_items'])}")
            logger.info(f"   Length: {len(journal_data['journal'])} chars")
            
            # Print action items
            if journal_data['action_items']:
                logger.info("   Action items:")
                for item in journal_data['action_items']:
                    logger.info(f"   - {item}")
        else:
            logger.warning("❌ No transcripts found for yesterday - journal not generated")
            return 1
        
    except Exception as e:
        logger.error(f"❌ Journal generation failed: {e}", exc_info=True)
        return 1
    
    logger.info("=== Daily Journal Generation Complete ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())
