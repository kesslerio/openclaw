"""
Memex HISTORIAN - Embeddings Manager
Handles text embedding generation using local sentence-transformers (no API costs)
"""

from typing import List
import logging

logger = logging.getLogger(__name__)

# Lazy load sentence-transformers to avoid slow import on module load
_model = None

def _get_model():
    """Lazy load the sentence-transformer model"""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        # all-MiniLM-L6-v2: Fast, good quality, 384 dimensions
        # all-mpnet-base-v2: Higher quality, 768 dimensions (slower)
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Loaded sentence-transformer model: all-MiniLM-L6-v2")
    return _model


class EmbeddingsManager:
    """
    Generates embeddings for text using local sentence-transformers.
    No API calls, runs entirely on local machine.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        logger.info(f"Initialized EmbeddingsManager with local model: {model_name}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            model = _get_model()
            embedding = model.encode(text, convert_to_numpy=True)
            logger.debug(f"Generated embedding for text (length: {len(text)})")
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in one batch.
        Much more efficient than calling generate_embedding() in a loop.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            model = _get_model()
            embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def estimate_cost(self, num_tokens: int) -> float:
        """
        Estimate cost for embedding generation.
        Local embeddings are FREE!

        Args:
            num_tokens: Estimated number of tokens

        Returns:
            Cost in USD (always 0 for local)
        """
        return 0.0  # Local embeddings have no API cost
