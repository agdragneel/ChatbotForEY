# AI Onboarding Chatbot System

A production-ready AI-powered onboarding chatbot built with Streamlit, HuggingFace Inference API, and RAG (Retrieval-Augmented Generation).

## Features

✅ **RAG-based Question Answering** - Retrieves relevant context from documents before generating answers
✅ **Multi-format Document Support** - Handles .txt, .pdf, .docx, .doc, images (.png, .jpg, .jpeg), and videos (.mp4)
✅ **Vision-powered Image Understanding** - Automatically captions images using Qwen VL model
✅ **Video Processing** - Extracts frames for visual analysis + transcribes audio with Whisper
✅ **FAISS Vector Search** - Fast and efficient similarity search
✅ **Interactive Chat Interface** - Clean Streamlit UI with chat history
✅ **Source Attribution** - Shows which documents were used to answer questions
✅ **User Feedback** - Thumbs up/down for response quality
✅ **Comprehensive Logging** - Track all operations for debugging

## Architecture

```
┌─────────────┐
│  Streamlit  │
│     UI      │
└──────┬──────┘
       │
┌──────▼──────┐
│ RAG System  │
└──────┬──────┘
       │
   ┌───┴────┬──────────┬──────────┐
   │        │          │          │
┌──▼───┐ ┌─▼────┐ ┌───▼────┐ ┌───▼────┐
│Loader│ │Vector│ │Embedding│ │HuggingF│
│      │ │Store │ │ Model  │ │ace API │
└──────┘ └──────┘ └────────┘ └────────┘
```

## Project Structure

```
ChatbotForEY/
├── app.py              # Main Streamlit application
├── rag.py              # RAG system orchestration
├── loader.py           # Document loading and chunking
├── embeddings.py       # Embedding generation
├── vector_store.py     # FAISS vector store
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── docs/               # Document storage (create this folder)
└── chatbot.log         # Application logs
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- HuggingFace account and API token

### 2. Get HuggingFace Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with read permissions
3. Copy the token

### 3. Installation

```bash
# Clone or navigate to the project directory
cd ChatbotForEY

# Install dependencies
pip install -r requirements.txt

# Set environment variable (Windows PowerShell)
$env:HF_TOKEN="your_huggingface_token_here"

# Or set it permanently in System Environment Variables
```

### 4. Add Documents

Create a `docs` folder and add your onboarding documents:

```bash
mkdir docs
```

Supported formats:
- `.txt` - Text files
- `.pdf` - PDF documents
- `.docx`, `.doc` - Word documents
- `.png`, `.jpg`, `.jpeg` - Images (will be auto-captioned)
- `.mp4` - Videos (frames analyzed + audio transcribed)

### 5. Run the Application

```bash
streamlit run app.py
```

The application will:
1. Automatically load all documents from the `docs` folder
2. Generate embeddings and build the vector index
3. Open in your browser at http://localhost:8501

## Usage

### Chat Interface

1. **Ask Questions** - Type your question in the chat input
2. **View Sources** - Click "Sources" to see which documents were used
3. **Provide Feedback** - Use 👍 or 👎 to rate responses
4. **Clear History** - Click "Clear Chat History" to start fresh

### Sidebar Features

- **System Status** - View loaded documents count and index status
- **Rebuild Vector Store** - Reindex documents after adding new files
- **Document List** - See all loaded documents

### Adding New Documents

1. Add new files to the `docs` folder
2. Click "Rebuild Vector Store" in the sidebar
3. Wait for indexing to complete
4. Start asking questions!

## Configuration

### Chunk Size

Modify in `loader.py`:
```python
def _chunk_text(self, text: str, source: str, chunk_size: int = 600, overlap: int = 100)
```

### Retrieval Count

Modify in `rag.py`:
```python
def query(self, question: str, top_k: int = 5)
```

### Model Parameters

Modify in `rag.py`:
```python
completion = self.client.chat.completions.create(
    model=self.model,
    max_tokens=1000,
    temperature=0.7,
)
```

## Logging

All operations are logged to:
- Console output
- `chatbot.log` file

Log levels:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Errors with stack traces

## Troubleshooting

### "HF_TOKEN environment variable is required"
- Make sure you've set the HF_TOKEN environment variable
- Restart your terminal/IDE after setting it

### "No documents found to index"
- Ensure the `docs` folder exists
- Add at least one supported document
- Click "Rebuild Vector Store"

### Image/Video captioning not working
- Verify HF_TOKEN is set correctly
- Check internet connection
- Review logs for API errors

### Video processing slow
- Videos are processed frame-by-frame with audio transcription
- Reduce `video_max_frames` or increase `video_frame_interval` in loader.py
- Use shorter videos for faster processing
- Check logs for detailed progress

### Slow performance
- Reduce chunk_size in loader.py
- Decrease top_k in query function
- Use fewer/smaller documents

## Security Notes

✅ HF_TOKEN is read from environment variables only
✅ No secrets are hardcoded
✅ No token logging
✅ Local-only operation (no external data storage)

## Model Information

- **LLM**: Qwen/Qwen2.5-VL-7B-Instruct:hyperbolic (via HuggingFace Router)
- **Vision Model**: Qwen/Qwen2.5-VL-7B-Instruct (for images and video frames)
- **Audio Transcription**: OpenAI Whisper (base model, runs locally)
- **Embeddings**: all-MiniLM-L6-v2 (sentence-transformers)
- **Vector Store**: FAISS (CPU version)

## License

This project is for internal use only.

## Support

For issues or questions, check the logs in `chatbot.log` for detailed error information.
