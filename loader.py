import os
import logging
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import PyPDF2
from PIL import Image
import base64
from io import BytesIO
from openai import OpenAI
import docx

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Handles loading and processing of various document types"""
    
    def __init__(self, docs_folder: str = "docs"):
        """
        Initialize document loader
        
        Args:
            docs_folder: Path to the documents folder
        """
        self.docs_folder = docs_folder
        self.loaded_files = []
        self.supported_extensions = ['.txt', '.pdf', '.png', '.jpg', '.jpeg', '.docx', '.doc']
        
        # Create docs folder if it doesn't exist
        os.makedirs(self.docs_folder, exist_ok=True)
        logger.info(f"Document loader initialized for folder: {self.docs_folder}")
        
        # Initialize OpenAI client for image captioning
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token:
            self.client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=hf_token,
            )
            self.vision_model = "Qwen/Qwen2.5-VL-7B-Instruct:hyperbolic"
            logger.info("Vision model initialized for image captioning")
        else:
            logger.warning("HF_TOKEN not set, image captioning will be disabled")
            self.client = None
    
    def load_all_documents(self) -> List[Dict[str, str]]:
        """
        Load all supported documents from the docs folder
        
        Returns:
            List of document chunks with metadata
        """
        logger.info(f"Scanning {self.docs_folder} for documents...")
        all_chunks = []
        self.loaded_files = []
        
        # Get all files in docs folder
        docs_path = Path(self.docs_folder)
        if not docs_path.exists():
            logger.warning(f"Docs folder {self.docs_folder} does not exist")
            return all_chunks
        
        files = list(docs_path.rglob("*"))
        logger.info(f"Found {len(files)} total files")
        
        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    logger.info(f"Processing file: {file_path.name}")
                    chunks = self._load_file(file_path)
                    all_chunks.extend(chunks)
                    self.loaded_files.append(file_path.name)
                    logger.info(f"Successfully loaded {file_path.name} ({len(chunks)} chunks)")
                except Exception as e:
                    logger.error(f"Error loading {file_path.name}: {str(e)}", exc_info=True)
        
        logger.info(f"Total documents loaded: {len(self.loaded_files)}, Total chunks: {len(all_chunks)}")
        return all_chunks
    
    def _load_file(self, file_path: Path) -> List[Dict[str, str]]:
        """
        Load a single file based on its extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of document chunks
        """
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            return self._load_text(file_path)
        elif extension == '.pdf':
            return self._load_pdf(file_path)
        elif extension in ['.png', '.jpg', '.jpeg']:
            return self._load_image(file_path)
        elif extension in ['.docx', '.doc']:
            return self._load_docx(file_path)
        else:
            logger.warning(f"Unsupported file type: {extension}")
            return []
    
    def _load_text(self, file_path: Path) -> List[Dict[str, str]]:
        """Load and chunk a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            chunks = self._chunk_text(text, file_path.name)
            return chunks
        except Exception as e:
            logger.error(f"Error loading text file {file_path.name}: {str(e)}", exc_info=True)
            return []
    
    def _load_pdf(self, file_path: Path) -> List[Dict[str, str]]:
        """Load and chunk a PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                logger.info(f"PDF has {len(pdf_reader.pages)} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n[Page {page_num + 1}]\n{page_text}"
            
            chunks = self._chunk_text(text, file_path.name)
            return chunks
        except Exception as e:
            logger.error(f"Error loading PDF {file_path.name}: {str(e)}", exc_info=True)
            return []
    
    def _load_image(self, file_path: Path) -> List[Dict[str, str]]:
        """Load an image and generate caption using vision model"""
        try:
            if not self.client:
                logger.warning(f"Cannot process image {file_path.name}: HF_TOKEN not set")
                return []
            
            logger.info(f"Generating caption for image: {file_path.name}")
            
            # Read and encode image
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Get image format
            image_format = file_path.suffix.lower().replace('.', '')
            if image_format == 'jpg':
                image_format = 'jpeg'
            
            # Generate caption using vision model
            try:
                completion = self.client.chat.completions.create(
                    model=self.vision_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Describe this image in detail. Focus on any text, diagrams, charts, or important information visible in the image."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/{image_format};base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=500,
                )
                
                caption = completion.choices[0].message.content
                logger.info(f"Generated caption for {file_path.name}")
                
                return [{
                    'text': f"[Image: {file_path.name}]\n{caption}",
                    'source': file_path.name,
                    'type': 'image'
                }]
                
            except Exception as e:
                logger.error(f"Error generating caption for {file_path.name}: {str(e)}", exc_info=True)
                # Fallback: just use filename
                return [{
                    'text': f"[Image: {file_path.name}]",
                    'source': file_path.name,
                    'type': 'image'
                }]
                
        except Exception as e:
            logger.error(f"Error loading image {file_path.name}: {str(e)}", exc_info=True)
            return []
    
    def _load_docx(self, file_path: Path) -> List[Dict[str, str]]:
        """Load and chunk a DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            
            for para in doc.paragraphs:
                text += para.text + "\n"
            
            logger.info(f"Extracted text from DOCX: {len(text)} characters")
            chunks = self._chunk_text(text, file_path.name)
            return chunks
        except Exception as e:
            logger.error(f"Error loading DOCX {file_path.name}: {str(e)}", exc_info=True)
            return []
    
    def _chunk_text(self, text: str, source: str, chunk_size: int = 600, overlap: int = 100) -> List[Dict[str, str]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            source: Source document name
            chunk_size: Target chunk size in characters (approximates tokens)
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks with metadata
        """
        if not text.strip():
            logger.warning(f"Empty text from {source}")
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings
                for sep in ['. ', '.\n', '! ', '?\n', '? ']:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep != -1:
                        end = last_sep + 1
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'source': source,
                    'type': 'text'
                })
            
            start = end - overlap
        
        logger.info(f"Created {len(chunks)} chunks from {source}")
        return chunks
