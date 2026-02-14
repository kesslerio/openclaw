"""
Daily Automation for Journal Generation
Handles scheduling, notifications, and data loading
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging
import os
import glob

from .config import (
    TRANSCRIPTS_DIR,
    JOURNALS_DIR,
    JOURNAL_TIME,
    NOTIFICATION_EMAIL,
    NOTIFICATION_TELEGRAM,
)
from .journal_generator import JournalGenerator

logger = logging.getLogger(__name__)


class DailyAutomation:
    """
    Automates daily journal generation.
    
    Features:
    - Load transcripts from file system
    - Generate journal for yesterday
    - Send notifications
    - Integration with cron/scheduler
    """
    
    def __init__(self, generator: Optional[JournalGenerator] = None):
        self.generator = generator or JournalGenerator()
        logger.info("Initialized DailyAutomation")
    
    def load_transcripts_for_date(self, date: str) -> List[Dict[str, Any]]:
        """
        Load all transcripts for a specific date.
        
        Args:
            date: Date string (YYYY-MM-DD)
        
        Returns:
            List of transcript dicts
        """
        transcripts_dir = Path(TRANSCRIPTS_DIR)
        
        # Find files matching date pattern: YYYY-MM-DD_*.txt
        pattern = f"{date}_*.txt"
        files = list(transcripts_dir.glob(pattern))
        
        logger.info(f"Found {len(files)} transcript files for {date}")
        
        transcripts = []
        for file_path in sorted(files):
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Extract metadata from filename and content
                metadata = self._extract_metadata(file_path, content)
                
                transcripts.append({
                    'content': content,
                    'metadata': metadata,
                    'file_path': str(file_path),
                })
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                continue
        
        return transcripts
    
    def _extract_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        Extract metadata from filename and content.
        
        Args:
            file_path: Path to transcript file
            content: Transcript content
        
        Returns:
            Metadata dict
        """
        import re
        
        filename = file_path.stem
        
        # Parse filename: YYYY-MM-DD_HH-MM_title
        parts = filename.split('_')
        date = parts[0] if len(parts) > 0 else 'Unknown'
        time = parts[1] if len(parts) > 1 else 'Unknown'
        title = '_'.join(parts[2:]) if len(parts) > 2 else 'Untitled'
        title = title.replace('_', ' ').strip()
        
        # Extract speaker from content
        speaker_match = re.search(r'^Speaker:\s*(.+)$', content, re.MULTILINE)
        speaker = speaker_match.group(1).strip() if speaker_match else 'Unknown'
        
        # Extract duration from content
        duration_match = re.search(r'Duration:\s*(\d+:\d+)', content)
        duration = duration_match.group(1) if duration_match else None
        
        return {
            'date': date,
            'time': time,
            'title': title,
            'speaker': speaker,
            'duration': duration,
            'word_count': len(content.split()),
        }
    
    def load_transcripts_by_date(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load transcripts grouped by date.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            Dict mapping dates to transcript lists
        """
        transcripts_dir = Path(TRANSCRIPTS_DIR)
        
        # Find all transcript files
        files = list(transcripts_dir.glob("*.txt"))
        
        logger.info(f"Found {len(files)} total transcript files")
        
        # Group by date
        by_date = {}
        
        for file_path in files:
            try:
                # Extract date from filename
                filename = file_path.stem
                date = filename.split('_')[0]
                
                # Apply date filters
                if start_date and date < start_date:
                    continue
                if end_date and date > end_date:
                    continue
                
                # Load transcript
                content = file_path.read_text(encoding='utf-8')
                metadata = self._extract_metadata(file_path, content)
                
                transcript = {
                    'content': content,
                    'metadata': metadata,
                    'file_path': str(file_path),
                }
                
                # Add to dict
                if date not in by_date:
                    by_date[date] = []
                by_date[date].append(transcript)
            
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                continue
        
        logger.info(f"Loaded transcripts for {len(by_date)} dates")
        return by_date
    
    def generate_daily_journal(self) -> Optional[Dict[str, Any]]:
        """
        Generate journal for yesterday (main automation function).
        
        Returns:
            Journal data dict or None
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        logger.info(f"Generating daily journal for {yesterday}")
        
        # Load transcripts
        transcripts = self.load_transcripts_for_date(yesterday)
        
        if not transcripts:
            logger.warning(f"No transcripts found for {yesterday}")
            return None
        
        # Generate journal
        try:
            journal_data = self.generator.generate_journal(yesterday, transcripts)
            file_path = self.generator.save_journal(journal_data)
            
            logger.info(f"Journal generated and saved to {file_path}")
            
            # Send notifications
            self._send_notifications(journal_data, file_path)
            
            return journal_data
        
        except Exception as e:
            logger.error(f"Journal generation failed: {e}")
            raise
    
    def _send_notifications(
        self,
        journal_data: Dict[str, Any],
        file_path: Path,
    ) -> None:
        """
        Send notifications about new journal.
        
        Args:
            journal_data: Generated journal data
            file_path: Path to saved journal
        """
        date = journal_data['date']
        action_count = len(journal_data['action_items'])
        
        message = f"""
📖 Daily Journal Generated

Date: {date}
Transcripts: {journal_data['transcript_count']}
Action Items: {action_count}
File: {file_path.name}

Preview:
{journal_data['journal'][:200]}...
""".strip()
        
        # Log notification (actual sending would be implemented separately)
        logger.info(f"Notification: {message}")
        
        # TODO: Integrate with existing notification systems
        # - Telegram bot
        # - Email (via himalaya or similar)
        # - WhatsApp
    
    def backfill_journals(
        self,
        start_date: str,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate journals for past dates (backfill).
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to yesterday
        
        Returns:
            List of generated journal data
        """
        if end_date is None:
            end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        logger.info(f"Backfilling journals from {start_date} to {end_date}")
        
        # Load transcripts
        transcripts_by_date = self.load_transcripts_by_date(start_date, end_date)
        
        # Generate journals
        journals = self.generator.generate_for_date_range(
            start_date=start_date,
            end_date=end_date,
            transcripts_by_date=transcripts_by_date,
        )
        
        logger.info(f"Backfill complete: {len(journals)} journals generated")
        return journals
    
    def get_journal_stats(self) -> Dict[str, Any]:
        """
        Get statistics about generated journals.
        
        Returns:
            Stats dict
        """
        journals_dir = Path(JOURNALS_DIR)
        journal_files = list(journals_dir.glob("*-journal.md"))
        
        if not journal_files:
            return {
                'total_journals': 0,
                'date_range': None,
            }
        
        # Extract dates
        dates = []
        for file_path in journal_files:
            date = file_path.stem.replace('-journal', '')
            dates.append(date)
        
        dates.sort()
        
        stats = {
            'total_journals': len(journal_files),
            'earliest_date': dates[0] if dates else None,
            'latest_date': dates[-1] if dates else None,
            'date_range': f"{dates[0]} to {dates[-1]}" if dates else None,
        }
        
        logger.info(f"Journal stats: {stats}")
        return stats
    
    @staticmethod
    def create_cron_command() -> str:
        """
        Generate cron command for daily automation.

        Returns:
            Cron command string
        """
        # Use MEMEX_BASE env var or a generic placeholder
        memex_base = os.getenv("MEMEX_BASE", "~/Cursor/Claude-2026/openclaw/skills/memex")
        script_path = f"{memex_base}/scripts/generate_daily_journal.py"

        # Parse journal time (HH:MM)
        hour, minute = JOURNAL_TIME.split(':')

        # Cron format: minute hour * * * command
        cron_command = f"{minute} {hour} * * * cd {memex_base} && python {script_path}"

        return cron_command
    
    @staticmethod
    def setup_automation_instructions() -> str:
        """
        Generate instructions for setting up automation.
        
        Returns:
            Setup instructions
        """
        cron_command = DailyAutomation.create_cron_command()
        
        memex_base = os.getenv("MEMEX_BASE", "~/Cursor/Claude-2026/openclaw/skills/memex")

        instructions = f"""
# Daily Journal Automation Setup

## Option 1: Cron (Traditional)

1. Create script: `{memex_base}/scripts/generate_daily_journal.py`

```python
#!/usr/bin/env python3
from journalist import DailyAutomation

automation = DailyAutomation()
automation.generate_daily_journal()
```

2. Make executable:
```bash
chmod +x {memex_base}/scripts/generate_daily_journal.py
```

3. Add to crontab:
```bash
crontab -e
# Add this line:
{cron_command}
```

## Option 2: Clawdbot Cron (Recommended)

Use Clawdbot's built-in cron system:

```javascript
// Add to Clawdbot config
{{
  "cron": {{
    "jobs": [
      {{
        "id": "daily-journal",
        "schedule": "{JOURNAL_TIME}",
        "text": "Generate yesterday's journal using Memex JOURNALIST. Load transcripts from data/transcripts/, generate journal, save to data/journals/, and notify me on Telegram.",
        "timezone": "America/Chicago"
      }}
    ]
  }}
}}
```

## Verification

Check if automation is working:
```bash
ls -lh {memex_base}/data/journals/
# Should see daily journal files
```
""".strip()
        
        return instructions
