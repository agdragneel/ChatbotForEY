# FFmpeg Installation Guide for Windows

## Why FFmpeg is Required

FFmpeg is required by OpenAI Whisper to extract audio from video files. Without it, Whisper cannot transcribe audio from .mp4 files, which is why you're seeing 0 audio segments.

## Installation Methods

### Method 1: Using Chocolatey (Recommended - Easiest)

If you have Chocolatey package manager installed:

```powershell
# Run PowerShell as Administrator
choco install ffmpeg
```

After installation, verify:
```powershell
ffmpeg -version
```

---

### Method 2: Using Winget (Windows Package Manager)

If you have Windows 10/11 with winget:

```powershell
# Run PowerShell as Administrator
winget install ffmpeg
```

After installation, verify:
```powershell
ffmpeg -version
```

---

### Method 3: Manual Installation (Most Reliable)

#### Step 1: Download FFmpeg

1. Go to: https://www.gyan.dev/ffmpeg/builds/
2. Download: **ffmpeg-release-essentials.zip** (under "Release builds")
3. Or direct link: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z

#### Step 2: Extract Files

1. Extract the downloaded archive to a permanent location
2. Recommended location: `C:\ffmpeg`
3. After extraction, you should have: `C:\ffmpeg\bin\ffmpeg.exe`

#### Step 3: Add to System PATH

**Option A: Using PowerShell (Run as Administrator)**

```powershell
# Add FFmpeg to system PATH
$ffmpegPath = "C:\ffmpeg\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$ffmpegPath", [EnvironmentVariableTarget]::Machine)

# Refresh current session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

**Option B: Using GUI**

1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "System variables", find and select "Path"
5. Click "Edit"
6. Click "New"
7. Add: `C:\ffmpeg\bin`
8. Click "OK" on all dialogs
9. **Restart PowerShell/Terminal**

#### Step 4: Verify Installation

Open a **new** PowerShell window and run:

```powershell
ffmpeg -version
```

You should see output like:
```
ffmpeg version N-xxxxx-gxxxxxxx
built with gcc x.x.x
configuration: ...
```

---

## After Installing FFmpeg

1. **Restart your terminal/PowerShell**
2. **Verify FFmpeg is accessible:**
   ```powershell
   ffmpeg -version
   ```

3. **Restart the Streamlit application:**
   ```powershell
   # Stop current app (Ctrl+C)
   .\start.ps1
   ```

4. **Rebuild the vector store** in the Streamlit UI

5. **Check the logs** - you should now see audio transcription working!

---

## Troubleshooting

### "ffmpeg is not recognized"

- Make sure you added the correct path to PATH
- The path should point to the `bin` folder (e.g., `C:\ffmpeg\bin`)
- Restart your terminal after adding to PATH
- Try opening a completely new PowerShell window

### "Access Denied" when setting PATH

- Run PowerShell as Administrator
- Or use the GUI method instead

### Still not working after installation

1. Check FFmpeg is in PATH:
   ```powershell
   $env:Path -split ';' | Select-String ffmpeg
   ```

2. Check FFmpeg executable exists:
   ```powershell
   Test-Path "C:\ffmpeg\bin\ffmpeg.exe"
   ```

3. Try running FFmpeg directly:
   ```powershell
   C:\ffmpeg\bin\ffmpeg.exe -version
   ```

---

## Quick Check Script

Run this to verify everything:

```powershell
# Check if FFmpeg is installed
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "✓ FFmpeg is installed" -ForegroundColor Green
    ffmpeg -version | Select-Object -First 1
} else {
    Write-Host "✗ FFmpeg is NOT installed" -ForegroundColor Red
    Write-Host "Please install FFmpeg using one of the methods above" -ForegroundColor Yellow
}
```

---

## Expected Behavior After Installation

Once FFmpeg is installed, when you process a video, you should see in the logs:

```
Starting audio transcription...
Loading Whisper model: base
Whisper model loaded successfully
Transcribing audio from video.mp4 with Whisper...
Detected language: en
Transcription complete: 15 segments  ← Should be > 0!
Full transcript length: 1234 characters
Transcript sample: Hello, welcome to...
```

The key indicator is **"Transcription complete: N segments"** where N > 0.
