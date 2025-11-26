"""
Startup script to verify the chatbot system is ready to run.
This script checks all dependencies and configurations before launching.
"""

import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if HF_TOKEN is set"""
    logger.info("Checking environment variables...")
    hf_token = os.environ.get("HF_TOKEN")
    
    if not hf_token:
        logger.error("❌ HF_TOKEN environment variable is not set!")
        logger.info("Please set it using: $env:HF_TOKEN='your_token_here'")
        return False
    
    logger.info(f"✅ HF_TOKEN is set (length: {len(hf_token)})")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    logger.info("Checking dependencies...")
    required_packages = [
        'streamlit',
        'openai',
        'sentence_transformers',
        'faiss',
        'PyPDF2',
        'PIL',
        'docx',
        'numpy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'docx':
                __import__('docx')
            else:
                __import__(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            logger.error(f"❌ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        logger.error(f"Missing packages: {', '.join(missing)}")
        logger.info("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_docs_folder():
    """Check if docs folder exists and has files"""
    logger.info("Checking docs folder...")
    docs_path = Path("docs")
    
    if not docs_path.exists():
        logger.error("❌ docs folder does not exist!")
        logger.info("Creating docs folder...")
        docs_path.mkdir(exist_ok=True)
        logger.info("✅ docs folder created")
        return True
    
    files = list(docs_path.rglob("*"))
    file_count = len([f for f in files if f.is_file()])
    
    if file_count == 0:
        logger.warning("⚠️  docs folder is empty - no documents to process")
        logger.info("Add some documents (.txt, .pdf, .docx, .jpg, .png) to the docs folder")
    else:
        logger.info(f"✅ Found {file_count} files in docs folder")
    
    return True

def check_project_files():
    """Check if all required project files exist"""
    logger.info("Checking project files...")
    required_files = [
        'app.py',
        'rag.py',
        'loader.py',
        'embeddings.py',
        'vector_store.py',
        'requirements.txt'
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            logger.error(f"❌ {file} is missing!")
            missing.append(file)
        else:
            logger.info(f"✅ {file} exists")
    
    if missing:
        logger.error(f"Missing files: {', '.join(missing)}")
        return False
    
    return True

def main():
    """Run all checks"""
    logger.info("=" * 60)
    logger.info("AI Onboarding Chatbot - System Check")
    logger.info("=" * 60)
    
    checks = [
        ("Project Files", check_project_files),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_environment),
        ("Documents Folder", check_docs_folder),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        logger.info(f"\n--- {check_name} ---")
        if not check_func():
            all_passed = False
    
    logger.info("\n" + "=" * 60)
    if all_passed:
        logger.info("✅ ALL CHECKS PASSED - System is ready!")
        logger.info("=" * 60)
        logger.info("\nTo start the chatbot, run:")
        logger.info("  streamlit run app.py")
        logger.info("\nOr use the PowerShell script:")
        logger.info("  .\\run.ps1")
        return 0
    else:
        logger.error("❌ SOME CHECKS FAILED - Please fix the issues above")
        logger.info("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
