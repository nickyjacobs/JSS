"""Whitelist and blacklist management."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

LISTS_DIR = Path(__file__).parent / "data"
WHITELIST_FILE = LISTS_DIR / "whitelist.json"
BLACKLIST_FILE = LISTS_DIR / "blacklist.json"


def ensure_lists_dir() -> Path:
    """Create lists directory if needed."""
    LISTS_DIR.mkdir(exist_ok=True)
    return LISTS_DIR


class ThreatLists:
    """Manages whitelist and blacklist."""

    def __init__(self) -> None:
        ensure_lists_dir()
        self.whitelist = self._load_list(WHITELIST_FILE)
        self.blacklist = self._load_list(BLACKLIST_FILE)

    def _load_list(self, file_path: Path) -> set[str]:
        """Load a list from JSON file."""
        if file_path.exists():
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    return set(data.get("indicators", []))
            except Exception as e:
                logger.error("Failed to load list %s: %s", file_path, e)
        return set()

    def _save_list(self, file_path: Path, indicators: set[str]) -> None:
        """Save a list to JSON file."""
        try:
            with open(file_path, "w") as f:
                json.dump({"indicators": sorted(list(indicators))}, f, indent=2)
        except Exception as e:
            logger.error("Failed to save list %s: %s", file_path, e)

    def is_whitelisted(self, indicator: str) -> bool:
        """Check if indicator is whitelisted."""
        return indicator in self.whitelist

    def is_blacklisted(self, indicator: str) -> bool:
        """Check if indicator is blacklisted."""
        return indicator in self.blacklist

    def add_whitelist(self, indicator: str) -> bool:
        """Add indicator to whitelist."""
        self.whitelist.add(indicator)
        self._save_list(WHITELIST_FILE, self.whitelist)
        return True

    def remove_whitelist(self, indicator: str) -> bool:
        """Remove indicator from whitelist."""
        if indicator in self.whitelist:
            self.whitelist.remove(indicator)
            self._save_list(WHITELIST_FILE, self.whitelist)
            return True
        return False

    def add_blacklist(self, indicator: str) -> bool:
        """Add indicator to blacklist."""
        self.blacklist.add(indicator)
        self._save_list(BLACKLIST_FILE, self.blacklist)
        return True

    def remove_blacklist(self, indicator: str) -> bool:
        """Remove indicator from blacklist."""
        if indicator in self.blacklist:
            self.blacklist.remove(indicator)
            self._save_list(BLACKLIST_FILE, self.blacklist)
            return True
        return False

    def get_all(self) -> dict[str, Any]:
        """Get all lists."""
        return {
            "whitelist": sorted(list(self.whitelist)),
            "blacklist": sorted(list(self.blacklist)),
        }

    def filter_threats(self, threats: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter threats based on whitelist/blacklist."""
        filtered = []
        for threat in threats:
            indicator = threat.get("indicator", "")
            if self.is_whitelisted(indicator):
                continue  # Skip whitelisted
            if self.is_blacklisted(indicator):
                threat["blacklisted"] = True
            filtered.append(threat)
        return filtered
