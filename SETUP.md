# AI Onboarding Chatbot - Setup Guide

Complete installation guide for Windows, Linux, and macOS.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Windows Setup](#windows-setup)
- [Linux Setup](#linux-setup)
- [macOS Setup](#macos-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

All platforms require:
- **Python 3.8 or higher**
- **Git** (for cloning the repository)
- **HuggingFace API Token** (free account at https://huggingface.co)

---

## Windows Setup

### Step 1: Install Python

1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. ✅ **Check "Add Python to PATH"**
4. Click "Install Now"
5. Verify installation:
   ```powershell
   python --version
   ```

### Step 2: Install FFmpeg

**Option A: Using Chocolatey (Recommended)**

```powershell
# Run PowerShell as Administrator
choco install ffmpeg -y
```

**Option B: Manual Installation**

1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Download **ffmpeg-release-essentials.zip**
3. Extract to `C:\ffmpeg`
4. Add to PATH:
   ```powershell
   # Run PowerShell as Administrator
   $ffmpegPath = "C:\ffmpeg\bin"
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$ffmpegPath", [EnvironmentVariableTarget]::Machine)
   ```
5. Restart PowerShell

**Verify FFmpeg:**
```powershell
ffmpeg -version
```

### Step 3: Clone Repository

```powershell
cd C:\Data\Programming
git clone <repository-url>
cd ChatbotForEY
```

### Step 4: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 5: Install Python Dependencies

```powershell
# Make sure virtual environment is activated
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Streamlit
- OpenAI
- Sentence Transformers
- FAISS
- PyPDF2
- Pillow
- python-docx
- python-dotenv
- opencv-python
- openai-whisper

### Step 6: Configure Environment

```powershell
# Copy example env file
copy .env.example .env

# Edit .env file and add your HuggingFace token
notepad .env
```

Add your token:
```
HF_TOKEN=your_huggingface_token_here
```

### Step 7: Create docs folder

```powershell
mkdir docs
```

Add your documents (.txt, .pdf, .docx, .jpg, .mp4) to this folder.

---

## Linux Setup

### Step 1: Install Python

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip -y
```

**Arch:**
```bash
sudo pacman -S python python-pip
```

**Verify:**
```bash
python3 --version
```

### Step 2: Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg -y
```

**Fedora/RHEL:**
```bash
sudo dnf install ffmpeg -y
```

**Arch:**
```bash
sudo pacman -S ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

### Step 3: Clone Repository

```bash
cd ~/Projects
git clone <repository-url>
cd ChatbotForEY
```

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### Step 5: Install Python Dependencies

```bash
# Make sure virtual environment is activated
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Add your token:
```
HF_TOKEN=your_huggingface_token_here
```

### Step 7: Create docs folder

```bash
mkdir -p docs
```

Add your documents to this folder.

---

## macOS Setup

### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Python

```bash
brew install python@3.11
```

**Verify:**
```bash
python3 --version
```

### Step 3: Install FFmpeg

```bash
brew install ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

### Step 4: Clone Repository

```bash
cd ~/Projects
git clone <repository-url>
cd ChatbotForEY
```

### Step 5: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### Step 6: Install Python Dependencies

```bash
# Make sure virtual environment is activated
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 7: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Add your token:
```
HF_TOKEN=your_huggingface_token_here
```

### Step 8: Create docs folder

```bash
mkdir -p docs
```

Add your documents to this folder.

---

## Configuration

### Get HuggingFace Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Give it a name (e.g., "chatbot")
4. Select "Read" permissions
5. Click "Generate"
6. Copy the token

### Add Token to .env

Edit the `.env` file and add your token:

```
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Supported Document Formats

Place documents in the `docs/` folder:
- `.txt` - Text files
- `.pdf` - PDF documents
- `.docx`, `.doc` - Word documents
- `.png`, `.jpg`, `.jpeg` - Images (auto-captioned)
- `.mp4` - Videos (frames analyzed + audio transcribed)

---

## Running the Application

### Windows

```powershell
# Activate virtual environment (if not already activated)
.\.venv\Scripts\Activate.ps1

# Run the application
python -m streamlit run app.py
```

Or use the startup script:
```powershell
.\start.ps1
```

### Linux/macOS

```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate

# Run the application
python -m streamlit run app.py
```

Or create a startup script:
```bash
#!/bin/bash
source .venv/bin/activate
python -m streamlit run app.py
```

Save as `start.sh`, make executable, and run:
```bash
chmod +x start.sh
./start.sh
```

### Access the Application

The application will automatically open in your browser at:
```
http://localhost:8501
```

---

## Troubleshooting

### Python not found

**Windows:**
- Reinstall Python and check "Add Python to PATH"
- Or add manually to PATH

**Linux/macOS:**
- Use `python3` instead of `python`
- Install Python using package manager

### FFmpeg not found

**Windows:**
- Verify PATH includes FFmpeg bin folder
- Restart terminal after adding to PATH

**Linux:**
- Install using package manager: `sudo apt install ffmpeg`

**macOS:**
- Install using Homebrew: `brew install ffmpeg`

### Virtual environment activation fails

**Windows:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/macOS:**
```bash
chmod +x .venv/bin/activate
```

### Module not found errors

```bash
# Activate virtual environment first
pip install -r requirements.txt
```

### HF_TOKEN not found

- Verify `.env` file exists in project root
- Check token is correctly formatted: `HF_TOKEN=hf_...`
- Restart the application after adding token

### Video processing shows 0 audio segments

- Verify FFmpeg is installed: `ffmpeg -version`
- Check video has audio track
- Review logs in `chatbot.log` for detailed errors

### Slow performance

- Reduce `video_max_frames` in `loader.py` (default: 50)
- Increase `video_frame_interval` (default: 5 seconds)
- Use smaller documents
- Reduce `top_k` in RAG queries

### Port 8501 already in use

```bash
# Kill existing Streamlit process
# Windows:
taskkill /F /IM streamlit.exe

# Linux/macOS:
pkill -f streamlit
```

Or use a different port:
```bash
streamlit run app.py --server.port 8502
```

---

## Verification Checklist

Before running the application, verify:

- [ ] Python 3.8+ installed: `python --version` or `python3 --version`
- [ ] FFmpeg installed: `ffmpeg -version`
- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip list | grep streamlit`
- [ ] `.env` file exists with HF_TOKEN
- [ ] `docs/` folder exists with documents
- [ ] All imports work: `python -c "import streamlit, openai, whisper, cv2"`

---

## Quick Start Commands

### Windows
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env and add HF_TOKEN
mkdir docs
python -m streamlit run app.py
```

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add HF_TOKEN
mkdir -p docs
python -m streamlit run app.py
```

---

## Next Steps

1. Add documents to `docs/` folder
2. Start the application
3. Wait for documents to be indexed
4. Start asking questions!

For more information, see [README.md](README.md)
