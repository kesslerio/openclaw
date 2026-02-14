"""
Prompt Engineering for Journal Generation
Crafts prompts that produce high-quality structured journals
"""

from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PromptEngineer:
    """
    Designs and refines prompts for journal generation.
    
    Key goals:
    - Structured markdown output
    - Action item extraction
    - Mermaid diagram generation
    - Conversational tone
    - Context preservation
    """
    
    SYSTEM_PROMPT = """You are a personal journal writer and executive assistant.

Your job is to transform voice transcripts into beautiful, structured daily journals.

**Your style:**
- Write in first person ("I discussed...", "We decided...")
- Be concise but capture key insights
- Extract actionable items
- Highlight important decisions
- Add helpful diagrams when appropriate

**Output format:**
Use clean markdown with:
- ## Headings for topics
- Bullet points for details
- **Bold** for key points
- Action items in a dedicated section
- Mermaid diagrams for complex ideas (mindmaps, flowcharts, sequences)

**Tone:** Professional but personal, like writing to your future self."""

    JOURNAL_PROMPT_TEMPLATE = """Generate a daily journal entry for {date}.

**Input transcripts from today:**

{transcripts}

**Instructions:**
1. Organize by topic/theme (not chronologically)
2. Extract key insights, decisions, and action items
3. Add a Mermaid diagram if the content involves:
   - Complex relationships → mindmap
   - Processes/workflows → flowchart
   - Conversations → sequence diagram
4. Write in first person
5. Be concise but insightful

**Output structure:**

# Daily Journal - {date}

## Summary
[2-3 sentence overview of the day]

## [Topic 1]
[Discussion and insights]

## [Topic 2]
[Discussion and insights]

## Action Items
- [ ] Action 1
- [ ] Action 2

## Diagram
```mermaid
[diagram if appropriate]
```

## Reflections
[Personal thoughts, lessons learned]
"""

    DIAGRAM_SELECTION_PROMPT = """Based on this content, suggest the best Mermaid diagram type:

{content}

Choose from:
- mindmap: For brainstorming, connected ideas, hierarchies
- graph: For relationships, networks, connections
- flowchart: For processes, decisions, workflows
- sequenceDiagram: For conversations, interactions, timelines

Respond with ONLY the diagram type, nothing else."""

    def __init__(self):
        logger.info("Initialized PromptEngineer")
    
    def create_journal_prompt(
        self,
        date: str,
        transcripts: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """
        Create a journal generation prompt from transcripts.
        
        Args:
            date: Date string (YYYY-MM-DD)
            transcripts: List of transcript dicts with 'content' and 'metadata'
        
        Returns:
            Dict with 'system' and 'user' prompts
        """
        # Format transcripts for prompt
        transcript_text = self._format_transcripts(transcripts)
        
        # Create user prompt
        user_prompt = self.JOURNAL_PROMPT_TEMPLATE.format(
            date=date,
            transcripts=transcript_text,
        )
        
        return {
            'system': self.SYSTEM_PROMPT,
            'user': user_prompt,
        }
    
    def _format_transcripts(self, transcripts: List[Dict[str, Any]]) -> str:
        """
        Format transcripts for inclusion in prompt.
        
        Args:
            transcripts: List of transcript dicts
        
        Returns:
            Formatted transcript text
        """
        if not transcripts:
            return "[No transcripts for this day]"
        
        formatted = []
        
        for i, t in enumerate(transcripts, 1):
            content = t.get('content', '')
            metadata = t.get('metadata', {})
            
            title = metadata.get('title', f'Recording {i}')
            time = metadata.get('time', 'Unknown time')
            speaker = metadata.get('speaker', 'Unknown')
            
            entry = f"""
### {i}. {title} ({time})
Speaker: {speaker}

{content}
"""
            formatted.append(entry)
        
        return "\n".join(formatted)
    
    def create_diagram_selection_prompt(self, content: str) -> Dict[str, str]:
        """
        Create prompt for diagram type selection.
        
        Args:
            content: Journal content to analyze
        
        Returns:
            Dict with 'system' and 'user' prompts
        """
        return {
            'system': "You are a diagram expert. Suggest the best Mermaid diagram type for given content.",
            'user': self.DIAGRAM_SELECTION_PROMPT.format(content=content),
        }
    
    def create_diagram_generation_prompt(
        self,
        content: str,
        diagram_type: str,
    ) -> Dict[str, str]:
        """
        Create prompt for diagram generation.
        
        Args:
            content: Content to visualize
            diagram_type: Type of Mermaid diagram
        
        Returns:
            Dict with 'system' and 'user' prompts
        """
        system = f"You are a Mermaid diagram expert. Generate {diagram_type} diagrams."
        
        user = f"""Create a Mermaid {diagram_type} diagram for this content:

{content}

Requirements:
- Use proper Mermaid syntax for {diagram_type}
- Keep it clean and readable
- Focus on key relationships/concepts
- Output ONLY the Mermaid code (no markdown fence, no explanations)

Example format:
{self._get_diagram_example(diagram_type)}
"""
        
        return {
            'system': system,
            'user': user,
        }
    
    def _get_diagram_example(self, diagram_type: str) -> str:
        """Get example diagram syntax for each type"""
        examples = {
            'mindmap': """mindmap
  root((Central Idea))
    Branch 1
      Subbranch 1.1
      Subbranch 1.2
    Branch 2""",
            
            'graph': """graph TD
    A[Start] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[Action 1]
    C -->|No| E[Action 2]""",
            
            'flowchart': """flowchart TD
    Start --> Process1
    Process1 --> Decision
    Decision -->|Yes| End1
    Decision -->|No| End2""",
            
            'sequenceDiagram': """sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob
    B->>A: Hello Alice"""
        }
        
        return examples.get(diagram_type, examples['graph'])
    
    def validate_journal_output(self, journal: str) -> bool:
        """
        Validate that generated journal meets quality standards.
        
        Args:
            journal: Generated journal text
        
        Returns:
            True if valid, False otherwise
        """
        # Check minimum length
        if len(journal) < 100:
            logger.warning("Journal too short")
            return False
        
        # Check for required sections
        required_sections = ['#', 'Summary', 'Action Items']
        if not all(section in journal for section in required_sections):
            logger.warning("Journal missing required sections")
            return False
        
        # Check for first person language
        first_person_indicators = ['I ', 'my ', 'we ', 'our ']
        if not any(indicator in journal.lower() for indicator in first_person_indicators):
            logger.warning("Journal not in first person")
            return False
        
        logger.info("Journal validation passed")
        return True
    
    def extract_action_items(self, journal: str) -> List[str]:
        """
        Extract action items from generated journal.
        
        Args:
            journal: Journal text
        
        Returns:
            List of action items
        """
        import re
        
        # Find action items section
        action_section_match = re.search(
            r'## Action Items\s+(.*?)(?=##|\Z)',
            journal,
            re.DOTALL | re.IGNORECASE
        )
        
        if not action_section_match:
            return []
        
        action_section = action_section_match.group(1)
        
        # Extract checkbox items
        items = re.findall(r'- \[ \] (.+)', action_section)
        
        logger.info(f"Extracted {len(items)} action items")
        return items
