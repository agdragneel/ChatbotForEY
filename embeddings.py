import logging
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingModel:
    """Handles text embedding generation using sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the sentence-transformer model to use
        """
        logger.info(f"Loading embedding model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded successfully. Dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}", exc_info=True)
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            Numpy array of embeddings
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}", exc_info=True)
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a batch of texts
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        try:
            logger.info(f"Embedding batch of {len(texts)} texts...")
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                batch_size=batch_size,
                show_progress_bar=True
            )
            logger.info(f"Successfully embedded {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding batch: {str(e)}", exc_info=True)
            raise
