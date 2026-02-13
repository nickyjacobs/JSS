"""
Configuration for File Type Identifier (FTI).
Use environment variable VIRUSTOTAL_API_KEY or .env – do not commit API keys.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Prefer environment variable so keys are never committed
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
