"""
Journal Generator
Orchestrates journal creation from transcripts using Claude
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sys
import anthropic

# Model enforcement
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.model_enforcer import ModelEnforcer, enforce_anthropic_only

from .config import (
    JOURNAL_TEMPERATURE,
    JOURNAL_MAX_TOKENS,
    JOURNALS_DIR,
    ENABLE_DIAGRAMS,
)
from .prompt_engineer import PromptEngineer

logger = logging.getLogger(__name__)

# Model enforcement - only Claude allowed
MODEL = enforce_anthropic_only("claude-sonnet-4-20250514")


class JournalGenerator:
    """
    Generates daily journals from voice transcripts using Claude.

    Features:
    - Structured markdown output
    - Action item extraction
    - Mermaid diagram generation
    - Quality validation
    """

    def __init__(
        self,
        model: str = MODEL,
        temperature: float = JOURNAL_TEMPERATURE,
        max_tokens: int = JOURNAL_MAX_TOKENS,
    ):
        self.model = ModelEnforcer.validate_model(model)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.prompt_engineer = PromptEngineer()
        self.client = ModelEnforcer.get_client()

        logger.info(f"Initialized JournalGenerator (model={self.model})")
    
    def generate_journal(
        self,
        date: str,
        transcripts: List[Dict[str, Any]],
        add_diagram: bool = ENABLE_DIAGRAMS,
    ) -> Dict[str, Any]:
        """
        Generate a journal entry for a specific date.
        
        Args:
            date: Date string (YYYY-MM-DD)
            transcripts: List of transcript dicts
            add_diagram: Whether to add Mermaid diagram
        
        Returns:
            Dict with 'journal', 'action_items', 'diagram' keys
        """
        logger.info(f"Generating journal for {date} ({len(transcripts)} transcripts)")
        
        # Create prompts
        prompts = self.prompt_engineer.create_journal_prompt(date, transcripts)
        
        # Generate journal
        journal = self._call_claude(
            system=prompts['system'],
            user=prompts['user'],
        )

        # Validate quality
        if not self.prompt_engineer.validate_journal_output(journal):
            logger.warning("Journal failed validation, retrying...")
            # Retry once
            journal = self._call_claude(
                system=prompts['system'],
                user=prompts['user'] + "\n\nIMPORTANT: Ensure the journal includes Summary, Action Items, and is written in first person.",
            )
        
        # Extract action items
        action_items = self.prompt_engineer.extract_action_items(journal)
        
        # Add diagram if enabled
        diagram_code = None
        if add_diagram and len(transcripts) > 0:
            try:
                diagram_code = self._generate_diagram(journal)
                if diagram_code:
                    # Insert diagram into journal if not already present
                    if 'mermaid' not in journal.lower():
                        journal = self._insert_diagram(journal, diagram_code)
            except Exception as e:
                logger.error(f"Diagram generation failed: {e}")
        
        result = {
            'journal': journal,
            'action_items': action_items,
            'diagram': diagram_code,
            'date': date,
            'transcript_count': len(transcripts),
            'generated_at': datetime.now().isoformat(),
        }
        
        logger.info(f"Journal generated successfully ({len(journal)} chars, {len(action_items)} actions)")
        return result
    
    def _call_claude(self, system: str, user: str) -> str:
        """
        Call Claude API.

        Args:
            system: System prompt
            user: User prompt

        Returns:
            Generated text
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system,
                messages=[
                    {"role": "user", "content": user},
                ],
            )

            content = response.content[0].text
            logger.debug(f"Claude response: {len(content)} chars")
            return content

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    def _generate_diagram(self, content: str) -> Optional[str]:
        """
        Generate a Mermaid diagram for journal content.

        Args:
            content: Journal content

        Returns:
            Mermaid diagram code or None
        """
        # Step 1: Determine best diagram type
        selection_prompts = self.prompt_engineer.create_diagram_selection_prompt(content)
        diagram_type = self._call_claude(
            system=selection_prompts['system'],
            user=selection_prompts['user'],
        ).strip().lower()

        # Validate diagram type
        valid_types = ['mindmap', 'graph', 'flowchart', 'sequencediagram']
        if diagram_type not in valid_types:
            logger.warning(f"Invalid diagram type: {diagram_type}, defaulting to graph")
            diagram_type = 'graph'

        logger.info(f"Selected diagram type: {diagram_type}")

        # Step 2: Generate diagram code
        diagram_prompts = self.prompt_engineer.create_diagram_generation_prompt(
            content=content[:1000],  # Limit to first 1000 chars for diagram
            diagram_type=diagram_type,
        )

        diagram_code = self._call_claude(
            system=diagram_prompts['system'],
            user=diagram_prompts['user'],
        ).strip()

        # Clean up diagram code (remove markdown fences if present)
        diagram_code = diagram_code.replace('```mermaid', '').replace('```', '').strip()

        return diagram_code
    
    def _insert_diagram(self, journal: str, diagram_code: str) -> str:
        """
        Insert diagram into journal at appropriate location.
        
        Args:
            journal: Original journal text
            diagram_code: Mermaid diagram code
        
        Returns:
            Journal with diagram inserted
        """
        # Find the best place to insert (after Summary, before Reflections)
        diagram_section = f"""
## Diagram

```mermaid
{diagram_code}
```
"""
        
        # Try to insert before Reflections section
        if '## Reflections' in journal:
            journal = journal.replace('## Reflections', diagram_section + '\n## Reflections')
        else:
            # Append to end
            journal += '\n' + diagram_section
        
        return journal
    
    def save_journal(
        self,
        journal_data: Dict[str, Any],
        output_dir: Path = JOURNALS_DIR,
    ) -> Path:
        """
        Save journal to markdown file.
        
        Args:
            journal_data: Dict from generate_journal()
            output_dir: Directory to save journal
        
        Returns:
            Path to saved journal file
        """
        date = journal_data['date']
        journal_text = journal_data['journal']
        
        # Create filename
        filename = f"{date}-journal.md"
        file_path = output_dir / filename
        
        # Add metadata header
        header = f"""---
date: {date}
generated_at: {journal_data['generated_at']}
transcript_count: {journal_data['transcript_count']}
action_items: {len(journal_data['action_items'])}
---

"""
        
        # Write file
        file_path.write_text(header + journal_text)
        
        logger.info(f"Journal saved to {file_path}")
        return file_path
    
    def generate_for_date_range(
        self,
        start_date: str,
        end_date: str,
        transcripts_by_date: Dict[str, List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """
        Generate journals for a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            transcripts_by_date: Dict mapping dates to transcript lists
        
        Returns:
            List of journal data dicts
        """
        from datetime import datetime, timedelta
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        journals = []
        current = start
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            transcripts = transcripts_by_date.get(date_str, [])
            
            if transcripts:
                try:
                    journal_data = self.generate_journal(date_str, transcripts)
                    self.save_journal(journal_data)
                    journals.append(journal_data)
                except Exception as e:
                    logger.error(f"Failed to generate journal for {date_str}: {e}")
            else:
                logger.info(f"No transcripts for {date_str}, skipping")
            
            current += timedelta(days=1)
        
        logger.info(f"Generated {len(journals)} journals for date range {start_date} to {end_date}")
        return journals
    
    def generate_yesterday(
        self,
        transcripts_by_date: Dict[str, List[Dict[str, Any]]],
    ) -> Optional[Dict[str, Any]]:
        """
        Generate journal for yesterday (common use case).
        
        Args:
            transcripts_by_date: Dict mapping dates to transcript lists
        
        Returns:
            Journal data dict or None
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        transcripts = transcripts_by_date.get(yesterday, [])
        
        if not transcripts:
            logger.info(f"No transcripts for yesterday ({yesterday})")
            return None
        
        journal_data = self.generate_journal(yesterday, transcripts)
        self.save_journal(journal_data)
        
        return journal_data
