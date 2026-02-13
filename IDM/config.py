"""
Configuration for Intrusion Detection Monitor (IDM)
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# Server (for future GUI)
SERVER_HOST = os.getenv("IDM_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("IDM_PORT", "8006"))

# Log paths (Linux)
AUTH_LOG = os.getenv("IDM_AUTH_LOG", "/var/log/auth.log")
SECURE_LOG = os.getenv("IDM_SECURE_LOG", "/var/log/secure")  # RHEL/CentOS

# Detection thresholds
FAILED_LOGIN_THRESHOLD = int(os.getenv("IDM_FAILED_LOGIN_THRESHOLD", "5"))
TIME_WINDOW_SECONDS = int(os.getenv("IDM_TIME_WINDOW", "300"))  # 5 min
ALERT_COOLDOWN_SECONDS = int(os.getenv("IDM_ALERT_COOLDOWN", "60"))
