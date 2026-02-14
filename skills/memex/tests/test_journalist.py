"""
Tests for JOURNALIST (Auto Journal Generator)
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from journalist.prompt_engineer import PromptEngineer
from journalist.journal_generator import JournalGenerator
from journalist.automation import DailyAutomation


class TestPromptEngineer:
    """Test prompt engineering"""
    
    @pytest.fixture
    def engineer(self):
        return PromptEngineer()
    
    def test_create_journal_prompt(self, engineer):
        """Test journal prompt creation"""
        transcripts = [
            {
                'content': 'Discussion about AI project',
                'metadata': {'title': 'AI Meeting', 'time': '10:00', 'speaker': 'Arvind'}
            }
        ]
        
        prompts = engineer.create_journal_prompt('2026-02-01', transcripts)
        
        assert 'system' in prompts
        assert 'user' in prompts
        assert '2026-02-01' in prompts['user']
        assert 'AI Meeting' in prompts['user']
    
    def test_format_transcripts(self, engineer):
        """Test transcript formatting"""
        transcripts = [
            {'content': 'Test 1', 'metadata': {'title': 'Meeting 1', 'time': '09:00'}},
            {'content': 'Test 2', 'metadata': {'title': 'Meeting 2', 'time': '14:00'}},
        ]
        
        formatted = engineer._format_transcripts(transcripts)
        
        assert 'Meeting 1' in formatted
        assert 'Meeting 2' in formatted
        assert '09:00' in formatted
    
    def test_validate_journal_output(self, engineer):
        """Test journal validation"""
        # Valid journal
        valid = """
# Daily Journal - 2026-02-01

## Summary
I discussed AI projects today.

## AI Project
We decided to use GPT-4.

## Action Items
- [ ] Review proposal
- [ ] Schedule meeting

## Reflections
Good progress made.
"""
        assert engineer.validate_journal_output(valid) == True
        
        # Invalid: too short
        assert engineer.validate_journal_output("Short text") == False
        
        # Invalid: missing sections
        invalid = "# Journal\n\nSome content but no required sections."
        assert engineer.validate_journal_output(invalid) == False
    
    def test_extract_action_items(self, engineer):
        """Test action item extraction"""
        journal = """
## Action Items
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Other Section
- Not an action item
"""
        
        items = engineer.extract_action_items(journal)
        
        assert len(items) == 3
        assert 'Task 1' in items
        assert 'Task 2' in items
        assert 'Not an action item' not in items


class TestJournalGenerator:
    """Test journal generation"""
    
    @pytest.fixture
    def generator(self):
        # Use a smaller model for testing if needed
        return JournalGenerator()
    
    def test_initialization(self, generator):
        """Test generator initializes correctly"""
        assert generator.model is not None
        assert generator.prompt_engineer is not None
    
    def test_generate_journal_structure(self, generator):
        """Test journal generation produces correct structure"""
        # Note: This test would call the actual GPT-4 API
        # In production, mock the API call or skip if no API key
        
        transcripts = [
            {
                'content': 'We discussed the new AI project. Key decision: use GPT-4 for summarization.',
                'metadata': {
                    'title': 'AI Project Meeting',
                    'time': '10:00',
                    'speaker': 'Arvind',
                    'date': '2026-02-01'
                }
            }
        ]
        
        # Skip if no API key (CI/CD)
        import os
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip("No OpenAI API key available")
        
        result = generator.generate_journal('2026-02-01', transcripts, add_diagram=False)
        
        assert 'journal' in result
        assert 'action_items' in result
        assert 'date' in result
        assert len(result['journal']) > 100
    
    def test_save_journal(self, generator, tmp_path):
        """Test saving journal to file"""
        journal_data = {
            'journal': '# Test Journal\n\nContent here',
            'action_items': ['Task 1', 'Task 2'],
            'date': '2026-02-01',
            'generated_at': datetime.now().isoformat(),
            'transcript_count': 1,
        }
        
        file_path = generator.save_journal(journal_data, output_dir=tmp_path)
        
        assert file_path.exists()
        assert '2026-02-01-journal.md' in str(file_path)
        
        content = file_path.read_text()
        assert 'Test Journal' in content
        assert 'date: 2026-02-01' in content


class TestDailyAutomation:
    """Test automation workflows"""
    
    @pytest.fixture
    def automation(self):
        return DailyAutomation()
    
    def test_initialization(self, automation):
        """Test automation initializes"""
        assert automation.generator is not None
    
    def test_extract_metadata_from_filename(self, automation, tmp_path):
        """Test metadata extraction"""
        file_path = tmp_path / "2026-02-01_10-30_meeting-notes.txt"
        content = "Speaker: Arvind Sarin\nDuration: 05:30\n\nContent here."
        file_path.write_text(content)
        
        metadata = automation._extract_metadata(file_path, content)
        
        assert metadata['date'] == '2026-02-01'
        assert metadata['time'] == '10-30'
        assert metadata['title'] == 'meeting notes'
        assert metadata['speaker'] == 'Arvind Sarin'
        assert metadata['duration'] == '05:30'
    
    def test_load_transcripts_for_date(self, automation, tmp_path, monkeypatch):
        """Test loading transcripts for a specific date"""
        # Mock TRANSCRIPTS_DIR
        monkeypatch.setattr('journalist.automation.TRANSCRIPTS_DIR', tmp_path)
        
        # Create test files
        (tmp_path / "2026-02-01_10-00_meeting1.txt").write_text("Content 1")
        (tmp_path / "2026-02-01_14-00_meeting2.txt").write_text("Content 2")
        (tmp_path / "2026-02-02_10-00_meeting3.txt").write_text("Content 3")
        
        transcripts = automation.load_transcripts_for_date('2026-02-01')
        
        assert len(transcripts) == 2
        assert all('content' in t for t in transcripts)
        assert all('metadata' in t for t in transcripts)
    
    def test_load_transcripts_by_date(self, automation, tmp_path, monkeypatch):
        """Test grouping transcripts by date"""
        monkeypatch.setattr('journalist.automation.TRANSCRIPTS_DIR', tmp_path)
        
        # Create test files for multiple dates
        (tmp_path / "2026-02-01_meeting1.txt").write_text("Content 1")
        (tmp_path / "2026-02-01_meeting2.txt").write_text("Content 2")
        (tmp_path / "2026-02-02_meeting3.txt").write_text("Content 3")
        
        by_date = automation.load_transcripts_by_date()
        
        assert len(by_date) == 2
        assert '2026-02-01' in by_date
        assert '2026-02-02' in by_date
        assert len(by_date['2026-02-01']) == 2
        assert len(by_date['2026-02-02']) == 1
    
    def test_get_journal_stats(self, automation, tmp_path, monkeypatch):
        """Test journal statistics"""
        monkeypatch.setattr('journalist.automation.JOURNALS_DIR', tmp_path)
        
        # Create test journal files
        (tmp_path / "2026-02-01-journal.md").write_text("Journal 1")
        (tmp_path / "2026-02-02-journal.md").write_text("Journal 2")
        (tmp_path / "2026-02-03-journal.md").write_text("Journal 3")
        
        stats = automation.get_journal_stats()
        
        assert stats['total_journals'] == 3
        assert stats['earliest_date'] == '2026-02-01'
        assert stats['latest_date'] == '2026-02-03'
    
    def test_create_cron_command(self):
        """Test cron command generation"""
        command = DailyAutomation.create_cron_command()
        
        assert '08:00' in command or command.startswith('0 8')  # 8 AM
        assert 'python' in command
        assert 'generate_daily_journal.py' in command
