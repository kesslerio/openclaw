"""
Memex HISTORIAN - Vector Store Manager
ChromaDB wrapper with CRUD operations
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
)

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Manages the ChromaDB vector database for transcript embeddings.
    Handles CRUD operations and metadata management.
    """
    
    def __init__(self, persist_directory: str = str(CHROMA_DIR)):
        """Initialize ChromaDB client and collection"""
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dimensions": EMBEDDING_DIMENSIONS,
                "created_at": datetime.now().isoformat(),
            }
        )
        
        logger.info(f"Initialized VectorStore with collection: {COLLECTION_NAME}")
        logger.info(f"Current document count: {self.collection.count()}")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None,
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of text chunks
            metadatas: List of metadata dicts (date, title, speaker, etc.)
            ids: List of unique IDs for each chunk
            embeddings: Optional pre-computed embeddings (will use ChromaDB default if None)
        """
        try:
            if embeddings:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=embeddings,
                )
            else:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                )
            
            logger.info(f"Added {len(documents)} documents to collection")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def query(
        self,
        query_texts: List[str],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query the vector store.
        
        Args:
            query_texts: List of query strings
            n_results: Number of results to return per query
            where: Metadata filters (e.g., {"date": {"$gte": "2026-01-01"}})
            where_document: Document content filters
        
        Returns:
            Query results with documents, metadatas, distances, and ids
        """
        try:
            results = self.collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document,
            )
            
            logger.info(f"Query returned {len(results['ids'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            raise
    
    def get_by_ids(self, ids: List[str]) -> Dict[str, Any]:
        """Get documents by their IDs"""
        try:
            results = self.collection.get(ids=ids)
            logger.info(f"Retrieved {len(results['ids'])} documents")
            return results
        except Exception as e:
            logger.error(f"Error getting documents by IDs: {e}")
            raise
    
    def update_metadata(self, id: str, metadata: Dict[str, Any]) -> None:
        """Update metadata for a document"""
        try:
            self.collection.update(ids=[id], metadatas=[metadata])
            logger.info(f"Updated metadata for document: {id}")
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            raise
    
    def delete_by_ids(self, ids: List[str]) -> None:
        """Delete documents by their IDs"""
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    def count(self) -> int:
        """Get total document count"""
        return self.collection.count()
    
    def reset(self) -> None:
        """⚠️ DANGER: Delete entire collection and recreate empty"""
        logger.warning("Resetting collection - all data will be lost!")
        self.client.delete_collection(name=COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dimensions": EMBEDDING_DIMENSIONS,
                "reset_at": datetime.now().isoformat(),
            }
        )
        logger.info("Collection reset complete")
