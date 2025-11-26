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
    
    def __init__(
        self, 
        docs_folder: str = "docs",
        video_frame_interval: int = 5,
        video_max_frames: int = 50,
        whisper_model: str = "base"
    ):
        """
        Initialize document loader
        
        Args:
            docs_folder: Path to the documents folder
            video_frame_interval: Seconds between frame extractions for videos
            video_max_frames: Maximum number of frames to extract per video
            whisper_model: Whisper model to use for audio transcription (base, small, medium, large)
        """
        self.docs_folder = docs_folder
        self.loaded_files = []
        self.supported_extensions = ['.txt', '.pdf', '.png', '.jpg', '.jpeg', '.docx', '.doc', '.mp4']
        self.video_frame_interval = video_frame_interval
        self.video_max_frames = video_max_frames
        self.whisper_model_name = whisper_model
        self.whisper_model = None  # Lazy load when needed
        
        # Create docs folder if it doesn't exist
        os.makedirs(self.docs_folder, exist_ok=True)
        logger.info(f"Document loader initialized for folder: {self.docs_folder}")
        logger.info(f"Video config: {video_frame_interval}s interval, max {video_max_frames} frames, Whisper: {whisper_model}")
        
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
        elif extension == '.mp4':
            return self._load_video(file_path)
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
    
    def _load_video(self, file_path: Path) -> List[Dict[str, str]]:
        """
        Load and process a video file by:
        1. Extracting and transcribing audio
        2. Extracting key frames and generating visual descriptions
        3. Combining both into a comprehensive summary
        """
        try:
            import cv2
            import whisper
            import tempfile
            import numpy as np
            
            logger.info(f"Processing video: {file_path.name}")
            
            if not self.client:
                logger.warning(f"Cannot process video {file_path.name}: HF_TOKEN not set")
                return []
            
            # Open video file
            video = cv2.VideoCapture(str(file_path))
            if not video.isOpened():
                logger.error(f"Failed to open video: {file_path.name}")
                return []
            
            # Get video properties
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count_total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count_total / fps if fps > 0 else 0
            
            logger.info(f"Video duration: {duration:.2f}s, FPS: {fps:.2f}, Total frames: {frame_count_total}")
            
            # PART 1: Audio Transcription
            transcript_segments = []
            try:
                logger.info("Starting audio transcription...")
                
                # Load Whisper model (lazy loading)
                if self.whisper_model is None:
                    logger.info(f"Loading Whisper model: {self.whisper_model_name}")
                    try:
                        self.whisper_model = whisper.load_model(self.whisper_model_name)
                        logger.info("Whisper model loaded successfully")
                    except Exception as model_error:
                        logger.error(f"Failed to load Whisper model: {str(model_error)}", exc_info=True)
                        raise
                
                # Transcribe audio directly from video file
                logger.info(f"Transcribing audio from {file_path.name} with Whisper...")
                logger.info(f"Video file path: {str(file_path)}")
                
                result = self.whisper_model.transcribe(
                    str(file_path),
                    verbose=True,  # Enable verbose for debugging
                    word_timestamps=False,
                    fp16=False  # Disable FP16 for compatibility
                )
                
                logger.info(f"Whisper transcription result keys: {result.keys()}")
                logger.info(f"Detected language: {result.get('language', 'unknown')}")
                
                transcript_segments = result.get('segments', [])
                full_text = result.get('text', '')
                
                logger.info(f"Transcription complete: {len(transcript_segments)} segments")
                logger.info(f"Full transcript length: {len(full_text)} characters")
                
                # Log sample of transcript
                if transcript_segments:
                    sample_text = transcript_segments[0]['text'][:100]
                    logger.info(f"Transcript sample: {sample_text}...")
                elif full_text:
                    logger.info(f"Full text sample: {full_text[:100]}...")
                else:
                    logger.warning("No transcript text found - video may not have audio")
                
            except Exception as e:
                logger.error(f"Audio transcription failed: {str(e)}", exc_info=True)
                logger.info("Continuing with video-only processing")
            
            # PART 2: Visual Frame Analysis
            frame_descriptions = []
            
            # Calculate frame extraction parameters
            frame_interval_frames = int(fps * self.video_frame_interval)
            total_frames_to_extract = min(
                self.video_max_frames,
                max(1, int(duration / self.video_frame_interval))
            )
            
            # Adjust interval if we would exceed max frames
            if total_frames_to_extract >= self.video_max_frames:
                frame_interval_frames = max(1, frame_count_total // self.video_max_frames)
            
            logger.info(f"Extracting {total_frames_to_extract} frames at {frame_interval_frames} frame intervals")
            
            frame_num = 0
            extracted_count = 0
            
            while extracted_count < total_frames_to_extract:
                # Set video position
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = video.read()
                
                if not ret:
                    break
                
                timestamp = frame_num / fps
                logger.info(f"Frame {extracted_count + 1}/{total_frames_to_extract}: Analyzing frame at {timestamp:.2f}s")
                
                try:
                    # Convert frame to JPEG
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Analyze frame with vision model
                    completion = self.client.chat.completions.create(
                        model=self.vision_model,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Describe what is shown in this video frame. Focus on key visual elements, actions, text, or important information."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{frame_base64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=300,
                    )
                    
                    description = completion.choices[0].message.content
                    frame_descriptions.append({
                        'timestamp': timestamp,
                        'description': description
                    })
                    
                    logger.info(f"Frame {extracted_count + 1} analyzed successfully")
                    
                except Exception as e:
                    logger.error(f"Error analyzing frame at {timestamp:.2f}s: {str(e)}")
                
                extracted_count += 1
                frame_num += frame_interval_frames
            
            video.release()
            logger.info(f"Frame extraction complete: {len(frame_descriptions)} frames analyzed")
            
            # PART 3: Combine Visual and Audio Data
            logger.info("Combining visual and audio data...")
            
            # Create comprehensive chunks
            chunks = []
            
            # Strategy: Create time-based chunks that combine nearby visual and audio
            chunk_duration = 30  # seconds per chunk
            num_chunks = max(1, int(duration / chunk_duration) + 1)
            
            for i in range(num_chunks):
                chunk_start = i * chunk_duration
                chunk_end = min((i + 1) * chunk_duration, duration)
                
                # Gather frames in this time range
                chunk_frames = [
                    f"[{fd['timestamp']:.1f}s] {fd['description']}"
                    for fd in frame_descriptions
                    if chunk_start <= fd['timestamp'] < chunk_end
                ]
                
                # Gather transcript segments in this time range
                chunk_transcript = [
                    f"[{seg['start']:.1f}s] {seg['text']}"
                    for seg in transcript_segments
                    if chunk_start <= seg['start'] < chunk_end
                ]
                
                # Only create chunk if there's content
                if chunk_frames or chunk_transcript:
                    chunk_text_parts = [f"[Video: {file_path.name}]"]
                    chunk_text_parts.append(f"[Time: {chunk_start:.1f}s - {chunk_end:.1f}s]")
                    
                    if chunk_frames:
                        chunk_text_parts.append("\nVisual Content:")
                        chunk_text_parts.extend(chunk_frames)
                    
                    if chunk_transcript:
                        chunk_text_parts.append("\nAudio Transcript:")
                        chunk_text_parts.extend(chunk_transcript)
                    
                    chunks.append({
                        'text': '\n'.join(chunk_text_parts),
                        'source': file_path.name,
                        'type': 'video',
                        'time_range': f"{chunk_start:.1f}s-{chunk_end:.1f}s"
                    })
            
            logger.info(f"Successfully processed video with {len(chunks)} chunks")
            logger.info(f"  - Visual frames: {len(frame_descriptions)}")
            logger.info(f"  - Audio segments: {len(transcript_segments)}")
            
            return chunks
            
        except ImportError as e:
            logger.error(f"Missing required library for video processing: {str(e)}")
            logger.error("Please install: pip install opencv-python openai-whisper")
            return []
        except Exception as e:
            logger.error(f"Error loading video {file_path.name}: {str(e)}", exc_info=True)
            return []

