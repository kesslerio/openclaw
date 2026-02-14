"""
Memex HISTORIAN - Text Processor
Handles transcript parsing, chunking, and metadata extraction
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import re
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter

from .config import CHUNK_SIZE, CHUNK_OVERLAP, METADATA_FIELDS

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Processes Plaud.AI transcripts:
    - Parses transcript files
    - Extracts metadata (date, title, speaker)
    - Chunks text for embedding
    - Generates unique IDs
    """
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        
        logger.info(f"Initialized TextProcessor (chunk_size={chunk_size}, overlap={chunk_overlap})")
    
    def parse_transcript_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a Plaud.AI transcript file and extract metadata.
        
        Args:
            file_path: Path to transcript file
        
        Returns:
            Dict with 'content', 'metadata' keys
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from filename: YYYY-MM-DD_title.txt
            metadata = self._extract_metadata_from_filename(file_path.name)
            
            # Extract additional metadata from content (if available)
            metadata.update(self._extract_metadata_from_content(content))
            
            metadata['source_file'] = str(file_path)
            
            logger.debug(f"Parsed transcript: {file_path.name}")
            return {
                'content': content,
                'metadata': metadata,
            }
        except Exception as e:
            logger.error(f"Error parsing transcript file {file_path}: {e}")
            raise
    
    def _extract_metadata_from_filename(self, filename: str) -> Dict[str, str]:
        """
        Extract metadata from filename format: YYYY-MM-DD_title.txt
        
        Args:
            filename: Filename string
        
        Returns:
            Dict with 'date', 'title'
        """
        metadata = {}
        
        # Match pattern: YYYY-MM-DD_title.txt
        pattern = r'^(\d{4}-\d{2}-\d{2})_(.+)\.txt$'
        match = re.match(pattern, filename)
        
        if match:
            metadata['date'] = match.group(1)
            title = match.group(2).replace('_', ' ').strip()
            metadata['title'] = title
        else:
            # Fallback: use filename as title
            metadata['date'] = datetime.now().strftime('%Y-%m-%d')
            metadata['title'] = filename.replace('.txt', '')
        
        return metadata
    
    def _extract_metadata_from_content(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from transcript content (speaker, duration, etc.)
        
        Args:
            content: Transcript text
        
        Returns:
            Dict with extracted metadata
        """
        metadata = {}
        
        # Extract speaker (if transcript has "Speaker: " format)
        speaker_match = re.search(r'^Speaker:\s*(.+)$', content, re.MULTILINE)
        if speaker_match:
            metadata['speaker'] = speaker_match.group(1).strip()
        else:
            metadata['speaker'] = 'Unknown'
        
        # Extract duration (if available in format "Duration: XX:XX")
        duration_match = re.search(r'Duration:\s*(\d+:\d+)', content)
        if duration_match:
            metadata['duration'] = duration_match.group(1)
        
        # Word count (rough indicator of content size)
        metadata['word_count'] = len(content.split())
        
        return metadata
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for embedding.
        
        Args:
            text: Full transcript text
        
        Returns:
            List of text chunks
        """
        chunks = self.text_splitter.split_text(text)
        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def prepare_for_vectorstore(
        self,
        file_path: Path,
    ) -> Tuple[List[str], List[Dict[str, Any]], List[str]]:
        """
        Complete processing pipeline: parse → chunk → prepare IDs and metadata.
        
        Args:
            file_path: Path to transcript file
        
        Returns:
            Tuple of (chunks, metadatas, ids)
        """
        # Parse file
        parsed = self.parse_transcript_file(file_path)
        content = parsed['content']
        base_metadata = parsed['metadata']
        
        # Chunk text
        chunks = self.chunk_text(content)
        
        # Generate IDs and metadata for each chunk
        ids = []
        metadatas = []
        
        for idx, chunk in enumerate(chunks):
            # Unique ID: filename_chunkN
            chunk_id = f"{file_path.stem}_chunk{idx}"
            ids.append(chunk_id)
            
            # Metadata: base metadata + chunk-specific info
            chunk_metadata = base_metadata.copy()
            chunk_metadata['chunk_index'] = idx
            chunk_metadata['chunk_count'] = len(chunks)
            chunk_metadata['chunk_size'] = len(chunk)
            
            metadatas.append(chunk_metadata)
        
        logger.info(f"Prepared {len(chunks)} chunks for {file_path.name}")
        return chunks, metadatas, ids
    
    def batch_prepare_files(
        self,
        file_paths: List[Path],
    ) -> Tuple[List[str], List[Dict[str, Any]], List[str]]:
        """
        Process multiple transcript files at once.
        
        Args:
            file_paths: List of paths to transcript files
        
        Returns:
            Tuple of (all_chunks, all_metadatas, all_ids)
        """
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        for file_path in file_paths:
            try:
                chunks, metadatas, ids = self.prepare_for_vectorstore(file_path)
                all_chunks.extend(chunks)
                all_metadatas.extend(metadatas)
                all_ids.extend(ids)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue
        
        logger.info(f"Batch prepared {len(file_paths)} files → {len(all_chunks)} chunks")
        return all_chunks, all_metadatas, all_ids
