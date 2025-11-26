import os
import logging
from datetime import datetime
from typing import List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from openai import OpenAI
from loader import DocumentLoader
from vector_store import VectorStore
from embeddings import EmbeddingModel

logger = logging.getLogger(__name__)

class RAGSystem:
    """Main RAG system orchestrating document loading, embedding, and querying"""
    
    def __init__(self):
        logger.info("Initializing RAG System...")
        self.docs_folder = "docs"
        self.loader = DocumentLoader(self.docs_folder)
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(self.embedding_model)
        self.vector_store_ready = False
        self.last_index_time = None
        
        # Initialize OpenAI client for HuggingFace
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            logger.error("HF_TOKEN environment variable not set!")
            raise ValueError("HF_TOKEN environment variable is required")
        
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_token,
        )
        self.model = "Qwen/Qwen2.5-VL-7B-Instruct:hyperbolic"
        logger.info(f"OpenAI client configured with model: {self.model}")
    
    def initialize(self):
        """Initialize the RAG system by loading documents and building vector store"""
        logger.info("Starting RAG system initialization...")
        try:
            # Load all documents
            logger.info(f"Loading documents from {self.docs_folder}...")
            documents = self.loader.load_all_documents()
            logger.info(f"Loaded {len(documents)} document chunks")
            
            if documents:
                # Build vector store
                logger.info("Building vector store...")
                self.vector_store.build_index(documents)
                self.vector_store_ready = True
                self.last_index_time = datetime.now()
                logger.info("Vector store built successfully")
            else:
                logger.warning("No documents found to index")
                self.vector_store_ready = False
                
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}", exc_info=True)
            self.vector_store_ready = False
            raise
    
    def rebuild_vector_store(self):
        """Rebuild the vector store from scratch"""
        logger.info("Rebuilding vector store...")
        self.vector_store_ready = False
        self.initialize()
    
    def query(self, question: str, top_k: int = 5) -> Tuple[str, List[str]]:
        """
        Query the RAG system
        
        Args:
            question: User's question
            top_k: Number of top documents to retrieve
            
        Returns:
            Tuple of (answer, list of source documents)
        """
        logger.info(f"Processing query: {question[:100]}...")
        
        if not self.vector_store_ready:
            logger.warning("Vector store not ready, returning error message")
            return "The system is not ready yet. Please wait for documents to be indexed.", []
        
        try:
            # Retrieve relevant documents
            logger.info(f"Retrieving top {top_k} relevant documents...")
            retrieved_docs = self.vector_store.search(question, top_k=top_k)
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            
            if not retrieved_docs:
                logger.warning("No relevant documents found")
                return "I couldn't find any relevant information to answer your question.", []
            
            # Extract context and sources
            context_parts = []
            sources = []
            
            for doc in retrieved_docs:
                context_parts.append(doc['text'])
                source = doc.get('source', 'Unknown')
                if source not in sources:
                    sources.append(source)
            
            context = "\n\n".join(context_parts)
            logger.info(f"Context prepared from {len(sources)} unique sources")
            
            # Build prompt
            system_prompt = """You are a helpful AI assistant for onboarding new employees. 
Your role is to answer questions based on the provided onboarding documentation.
Be friendly, clear, and concise. If the context doesn't contain enough information 
to answer the question, say so politely."""

            user_prompt = f"""Based on the following context from onboarding documents, please answer the question.

Context:
{context}

Question: {question}

Answer:"""
            
            # Call HuggingFace API
            logger.info("Calling HuggingFace API...")
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            
            answer = completion.choices[0].message.content
            logger.info("Response generated successfully")
            
            return answer, sources
            
        except Exception as e:
            logger.error(f"Error during query: {str(e)}", exc_info=True)
            return f"An error occurred while processing your question: {str(e)}", []
    
    def get_document_count(self) -> int:
        """Get the number of loaded documents"""
        return len(self.loader.loaded_files)
    
    def get_loaded_documents(self) -> List[str]:
        """Get list of loaded document names"""
        return sorted(self.loader.loaded_files)
