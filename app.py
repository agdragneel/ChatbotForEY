import streamlit as st
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from rag import RAGSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Onboarding Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'rag_system' not in st.session_state:
    logger.info("Initializing RAG system...")
    st.session_state.rag_system = RAGSystem()
    st.session_state.rag_system.initialize()
    logger.info("RAG system initialized successfully")

if 'messages' not in st.session_state:
    st.session_state.messages = []
    logger.info("Chat history initialized")

if 'feedback' not in st.session_state:
    st.session_state.feedback = {}

# Sidebar
with st.sidebar:
    st.title("📊 System Status")
    
    # Vector store status
    rag_system = st.session_state.rag_system
    
    st.metric("Loaded Documents", rag_system.get_document_count())
    
    vector_status = "✅ Ready" if rag_system.vector_store_ready else "❌ Not Ready"
    st.metric("Vector Index Status", vector_status)
    
    if rag_system.last_index_time:
        st.metric("Last Indexed", rag_system.last_index_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    st.divider()
    
    # Rebuild button
    if st.button("🔄 Rebuild Vector Store", use_container_width=True):
        logger.info("User requested vector store rebuild")
        with st.spinner("Rebuilding vector store..."):
            try:
                rag_system.rebuild_vector_store()
                st.success("Vector store rebuilt successfully!")
                logger.info("Vector store rebuilt successfully")
                st.rerun()
            except Exception as e:
                st.error(f"Error rebuilding vector store: {str(e)}")
                logger.error(f"Error rebuilding vector store: {str(e)}", exc_info=True)
    
    st.divider()
    
    # Document list
    st.subheader("📁 Loaded Documents")
    docs = rag_system.get_loaded_documents()
    if docs:
        for doc in docs:
            st.text(f"• {doc}")
    else:
        st.info("No documents loaded")
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        logger.info("Chat history cleared")
        st.rerun()

# Main chat interface
st.title("🤖 AI Onboarding Chatbot")
st.markdown("Ask me anything about the onboarding documents!")

# Display chat messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display sources for assistant messages
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.text(f"• {source}")
        
        # Display feedback buttons for assistant messages
        if message["role"] == "assistant":
            col1, col2, col3 = st.columns([1, 1, 10])
            with col1:
                if st.button("👍", key=f"up_{idx}"):
                    st.session_state.feedback[idx] = "positive"
                    logger.info(f"Positive feedback for message {idx}")
                    st.success("Thanks for your feedback!")
            with col2:
                if st.button("👎", key=f"down_{idx}"):
                    st.session_state.feedback[idx] = "negative"
                    logger.info(f"Negative feedback for message {idx}")
                    st.info("Thanks for your feedback!")

# Chat input
if prompt := st.chat_input("Ask a question about onboarding..."):
    logger.info(f"User query: {prompt}")
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                logger.info("Generating response...")
                response, sources = rag_system.query(prompt)
                logger.info(f"Response generated with {len(sources)} sources")
                
                st.markdown(response)
                
                # Display sources
                if sources:
                    with st.expander("📚 Sources"):
                        for source in sources:
                            st.text(f"• {source}")
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources
                })
                
            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                st.error(error_msg)
                logger.error(error_msg, exc_info=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I apologize, but I encountered an error processing your request. Please try again."
                })

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    Powered by HuggingFace Inference API | Qwen/Qwen2.5-VL-7B-Instruct
    </div>
    """,
    unsafe_allow_html=True
)
