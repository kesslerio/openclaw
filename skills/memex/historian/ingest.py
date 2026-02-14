"""
Memex HISTORIAN - Ingestion Pipeline
Orchestrates the full ingestion flow:
Parse → Chunk → Embed → Store
"""

from pathlib import Path
from typing import List, Optional
import logging
from tqdm import tqdm

from .text_processor import TextProcessor
from .embeddings import EmbeddingsManager
from .vector_store import VectorStore
from .config import TRANSCRIPTS_DIR

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Complete pipeline for ingesting Plaud.AI transcripts into the vector store.
    
    Flow:
        1. Parse transcript files (TextProcessor)
        2. Chunk text into manageable pieces
        3. Generate embeddings (EmbeddingsManager)
        4. Store in ChromaDB (VectorStore)
    """
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        text_processor: Optional[TextProcessor] = None,
        embeddings_manager: Optional[EmbeddingsManager] = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.text_processor = text_processor or TextProcessor()
        self.embeddings_manager = embeddings_manager or EmbeddingsManager()
        
        logger.info("Initialized IngestionPipeline")
    
    def ingest_file(self, file_path: Path, generate_embeddings: bool = True) -> int:
        """
        Ingest a single transcript file.
        
        Args:
            file_path: Path to transcript file
            generate_embeddings: If False, let ChromaDB generate embeddings
        
        Returns:
            Number of chunks ingested
        """
        try:
            # Parse and chunk
            chunks, metadatas, ids = self.text_processor.prepare_for_vectorstore(file_path)
            
            # Generate embeddings (optional - ChromaDB can do this automatically)
            embeddings = None
            if generate_embeddings:
                logger.info(f"Generating embeddings for {len(chunks)} chunks...")
                embeddings = self.embeddings_manager.generate_embeddings_batch(chunks)
            
            # Store in vector database
            self.vector_store.add_documents(
                documents=chunks,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings,
            )
            
            logger.info(f"✅ Ingested {file_path.name} ({len(chunks)} chunks)")
            return len(chunks)
        
        except Exception as e:
            logger.error(f"❌ Error ingesting {file_path}: {e}")
            raise
    
    def ingest_directory(
        self,
        directory: Path = TRANSCRIPTS_DIR,
        pattern: str = "*.txt",
        generate_embeddings: bool = True,
        show_progress: bool = True,
    ) -> dict:
        """
        Ingest all transcript files from a directory.
        
        Args:
            directory: Directory containing transcript files
            pattern: File pattern to match (default: *.txt)
            generate_embeddings: If False, let ChromaDB handle embeddings
            show_progress: Show progress bar
        
        Returns:
            Dict with ingestion statistics
        """
        # Find all matching files
        files = list(Path(directory).glob(pattern))
        
        if not files:
            logger.warning(f"No files found matching {pattern} in {directory}")
            return {
                'total_files': 0,
                'total_chunks': 0,
                'successful': 0,
                'failed': 0,
            }
        
        logger.info(f"Found {len(files)} files to ingest")
        
        stats = {
            'total_files': len(files),
            'total_chunks': 0,
            'successful': 0,
            'failed': 0,
            'failed_files': [],
        }
        
        # Process files with progress bar
        iterator = tqdm(files, desc="Ingesting transcripts") if show_progress else files
        
        for file_path in iterator:
            try:
                num_chunks = self.ingest_file(file_path, generate_embeddings)
                stats['total_chunks'] += num_chunks
                stats['successful'] += 1
            except Exception as e:
                stats['failed'] += 1
                stats['failed_files'].append(str(file_path))
                logger.error(f"Failed to ingest {file_path}: {e}")
                continue
        
        # Final summary
        logger.info(f"""
        📊 Ingestion Complete!
        =====================
        Total files: {stats['total_files']}
        Successful: {stats['successful']}
        Failed: {stats['failed']}
        Total chunks: {stats['total_chunks']}
        """)
        
        return stats
    
    def ingest_batch(
        self,
        file_paths: List[Path],
        batch_size: int = 100,
        generate_embeddings: bool = True,
    ) -> dict:
        """
        Ingest files in batches for efficiency.
        
        Args:
            file_paths: List of file paths to ingest
            batch_size: Number of files to process in each batch
            generate_embeddings: If False, let ChromaDB handle embeddings
        
        Returns:
            Dict with ingestion statistics
        """
        stats = {
            'total_files': len(file_paths),
            'total_chunks': 0,
            'successful': 0,
            'failed': 0,
        }
        
        # Process in batches
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} files)")
            
            try:
                # Batch prepare
                all_chunks, all_metadatas, all_ids = self.text_processor.batch_prepare_files(batch)
                
                # Generate embeddings
                embeddings = None
                if generate_embeddings:
                    embeddings = self.embeddings_manager.generate_embeddings_batch(all_chunks)
                
                # Store batch
                self.vector_store.add_documents(
                    documents=all_chunks,
                    metadatas=all_metadatas,
                    ids=all_ids,
                    embeddings=embeddings,
                )
                
                stats['total_chunks'] += len(all_chunks)
                stats['successful'] += len(batch)
                logger.info(f"✅ Batch complete: {len(batch)} files, {len(all_chunks)} chunks")
            
            except Exception as e:
                stats['failed'] += len(batch)
                logger.error(f"❌ Batch failed: {e}")
                continue
        
        logger.info(f"📊 Batch ingestion complete: {stats}")
        return stats
