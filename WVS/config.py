"""
Configuration for Web Vulnerability Scanner
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# Server configuration
SERVER_HOST = os.getenv("WVS_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("WVS_PORT", "8004"))

# Scanner configuration
DEFAULT_TIMEOUT = int(os.getenv("WVS_TIMEOUT", "10"))  # seconds
MAX_CONCURRENT_REQUESTS = int(os.getenv("WVS_MAX_CONCURRENT", "10"))
USER_AGENT = os.getenv("WVS_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

# Scan settings
ENABLE_SQL_INJECTION = os.getenv("WVS_ENABLE_SQL", "true").lower() == "true"
ENABLE_XSS = os.getenv("WVS_ENABLE_XSS", "true").lower() == "true"
ENABLE_DIRECTORY_TRAVERSAL = os.getenv("WVS_ENABLE_DIR_TRAV", "true").lower() == "true"
ENABLE_COMMAND_INJECTION = os.getenv("WVS_ENABLE_CMD_INJ", "true").lower() == "true"
ENABLE_FILE_UPLOAD = os.getenv("WVS_ENABLE_FILE_UPLOAD", "true").lower() == "true"

# Results storage
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)
