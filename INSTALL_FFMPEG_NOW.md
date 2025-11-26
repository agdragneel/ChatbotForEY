# Quick FFmpeg Installation

## ✅ You have Chocolatey installed!

This is the easiest way to install FFmpeg.

## Installation Command

Run this command in **PowerShell as Administrator**:

```powershell
choco install ffmpeg -y
```

The `-y` flag automatically confirms the installation.

## After Installation

1. **Verify FFmpeg is installed:**
   ```powershell
   ffmpeg -version
   ```

2. **Restart your Streamlit app:**
   - Press Ctrl+C in the terminal running Streamlit
   - Run: `.\start.ps1`

3. **Rebuild the vector store** in the Streamlit UI

4. **Check the logs** - audio segments should now be > 0!

## Alternative: If you don't have admin access

Use the manual installation method from `FFMPEG_INSTALL.md`
