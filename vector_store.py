import logging
import numpy as np
import faiss
from typing import List, Dict
from embeddings import EmbeddingModel

logger = logging.getLogger(__name__)

class VectorStore:
    """FAISS-based vector store for document retrieval"""
    
    def __init__(self, embedding_model: EmbeddingModel):
        """
        Initialize vector store
        
        Args:
            embedding_model: Embedding model instance
        """
        self.embedding_model = embedding_model
        self.index = None
        self.documents = []
        self.dimension = embedding_model.embedding_dim
        logger.info(f"Vector store initialized with dimension: {self.dimension}")
    
    def build_index(self, documents: List[Dict[str, str]]):
        """
        Build FAISS index from documents
        
        Args:
            documents: List of document chunks with metadata
        """
        if not documents:
            logger.warning("No documents to index")
            return
        
        logger.info(f"Building FAISS index for {len(documents)} documents...")
        
        try:
            # Extract texts
            texts = [doc['text'] for doc in documents]
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            embeddings = self.embedding_model.embed_batch(texts)
            
            # Create FAISS index
            logger.info("Creating FAISS index...")
            self.index = faiss.IndexFlatL2(self.dimension)
            
            # Add vectors to index
            self.index.add(embeddings.astype('float32'))
            
            # Store documents
            self.documents = documents
            
            logger.info(f"FAISS index built successfully with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Error building index: {str(e)}", exc_info=True)
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of top-k most similar documents
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty or not built")
            return []
        
        try:
            logger.info(f"Searching for: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = self.embedding_model.embed_text(query)
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            
            # Search
            k = min(top_k, self.index.ntotal)
            distances, indices = self.index.search(query_embedding, k)
            
            # Retrieve documents
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    doc['distance'] = float(distance)
                    results.append(doc)
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}", exc_info=True)
            return []
    
    def get_index_size(self) -> int:
        """Get the number of vectors in the index"""
        if self.index is None:
            return 0
        return self.index.ntotal
