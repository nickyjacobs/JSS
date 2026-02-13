"""
Configuration for Secure File Sharing System
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# Server configuration
SERVER_HOST = os.getenv("SFS_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SFS_PORT", "8003"))

# File storage
STORAGE_DIR = Path(__file__).parent / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

UPLOAD_DIR = STORAGE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

METADATA_DIR = STORAGE_DIR / "metadata"
METADATA_DIR.mkdir(exist_ok=True)

DOWNLOAD_DIR = STORAGE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Security settings
MAX_FILE_SIZE = int(os.getenv("SFS_MAX_FILE_SIZE", "100")) * 1024 * 1024  # Default 100MB
TOKEN_LENGTH = int(os.getenv("SFS_TOKEN_LENGTH", "32"))
DEFAULT_EXPIRY_HOURS = int(os.getenv("SFS_DEFAULT_EXPIRY", "24"))

# Encryption
ENCRYPTION_KEY_FILE = STORAGE_DIR / ".encryption_key"
if not ENCRYPTION_KEY_FILE.exists():
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    ENCRYPTION_KEY_FILE.write_bytes(key)
