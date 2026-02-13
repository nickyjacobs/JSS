"""
Configuration for DoS Attack Detector
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# Server configuration
SERVER_HOST = os.getenv("DSAD_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("DSAD_PORT", "8005"))

# Default detector thresholds
DEFAULT_SYN_THRESHOLD = int(os.getenv("DSAD_SYN_THRESHOLD", "100"))
DEFAULT_UDP_THRESHOLD = int(os.getenv("DSAD_UDP_THRESHOLD", "200"))
DEFAULT_ICMP_THRESHOLD = int(os.getenv("DSAD_ICMP_THRESHOLD", "150"))
DEFAULT_HTTP_THRESHOLD = int(os.getenv("DSAD_HTTP_THRESHOLD", "300"))
DEFAULT_TIME_WINDOW = int(os.getenv("DSAD_TIME_WINDOW", "10"))
