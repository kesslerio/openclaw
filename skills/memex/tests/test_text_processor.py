"""
Tests for Text Processor
"""

import pytest
from pathlib import Path

from historian.text_processor import TextProcessor


class TestTextProcessor:
    """Test transcript parsing and chunking"""
    
    @pytest.fixture
    def processor(self):
        return TextProcessor(chunk_size=100, chunk_overlap=10)
    
    @pytest.fixture
    def sample_transcript(self, tmp_path):
        """Create a sample transcript file"""
        file_path = tmp_path / "2026-02-01_test-recording.txt"
        content = """Speaker: Arvind Sarin
Duration: 05:30

This is a test transcript about building Memex.
The system will use ChromaDB for vector storage.
It will have recency ranking to prioritize recent memories.

We discussed the architecture and decided to use FastAPI for the REST API.
The frontend will be built with React and TailwindCSS.
"""
        file_path.write_text(content)
        return file_path
    
    def test_parse_transcript_file(self, processor, sample_transcript):
        """Test parsing a transcript file"""
        result = processor.parse_transcript_file(sample_transcript)
        
        assert 'content' in result
        assert 'metadata' in result
        assert len(result['content']) > 0
        assert result['metadata']['date'] == '2026-02-01'
        assert result['metadata']['title'] == 'test recording'
    
    def test_extract_metadata_from_filename(self, processor):
        """Test metadata extraction from filename"""
        metadata = processor._extract_metadata_from_filename("2026-02-01_meeting-notes.txt")
        
        assert metadata['date'] == '2026-02-01'
        assert metadata['title'] == 'meeting notes'
    
    def test_extract_speaker_from_content(self, processor, sample_transcript):
        """Test speaker extraction from content"""
        result = processor.parse_transcript_file(sample_transcript)
        
        assert result['metadata']['speaker'] == 'Arvind Sarin'
    
    def test_extract_duration_from_content(self, processor, sample_transcript):
        """Test duration extraction from content"""
        result = processor.parse_transcript_file(sample_transcript)
        
        assert result['metadata']['duration'] == '05:30'
    
    def test_chunk_text(self, processor):
        """Test text chunking"""
        long_text = "This is a sentence. " * 50  # 1000 chars
        
        chunks = processor.chunk_text(long_text)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 110 for chunk in chunks)  # chunk_size + small buffer
    
    def test_prepare_for_vectorstore(self, processor, sample_transcript):
        """Test complete processing pipeline"""
        chunks, metadatas, ids = processor.prepare_for_vectorstore(sample_transcript)
        
        assert len(chunks) == len(metadatas) == len(ids)
        assert all('chunk_index' in meta for meta in metadatas)
        assert all('date' in meta for meta in metadatas)
        assert all(id_.startswith('2026-02-01_test-recording') for id_ in ids)
    
    def test_chunk_metadata_includes_index(self, processor, sample_transcript):
        """Test that chunks have index metadata"""
        chunks, metadatas, ids = processor.prepare_for_vectorstore(sample_transcript)
        
        for idx, meta in enumerate(metadatas):
            assert meta['chunk_index'] == idx
            assert meta['chunk_count'] == len(chunks)
    
    def test_batch_prepare_files(self, processor, tmp_path):
        """Test processing multiple files"""
        # Create multiple test files
        files = []
        for i in range(3):
            file_path = tmp_path / f"2026-02-0{i+1}_test-{i}.txt"
            file_path.write_text(f"Test transcript {i+1}")
            files.append(file_path)
        
        all_chunks, all_metas, all_ids = processor.batch_prepare_files(files)
        
        assert len(all_chunks) >= 3  # At least one chunk per file
        assert len(all_chunks) == len(all_metas) == len(all_ids)
