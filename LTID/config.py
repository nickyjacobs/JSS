"""Configuration for the Threat Intelligence Dashboard."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Always load .env from LTID directory, regardless of where script is run from
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Fallback to default behavior
        load_dotenv()
except ImportError:
    pass


class Config:
    """Central configuration."""

    # API Keys (required for full functionality)
    ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY", "")
    OTX_API_KEY = os.getenv("OTX_API_KEY", "")
    VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")

    # Dashboard
    HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    PORT = int(os.getenv("DASHBOARD_PORT", "8001"))  # Changed from 8000 to avoid conflict with FTI
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))
