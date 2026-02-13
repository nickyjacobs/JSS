"""Input validation and data quality checks."""
from __future__ import annotations

import ipaddress
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def is_valid_ip(ip: str) -> bool:
    """Validate IP address (IPv4 or IPv6)."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_domain(domain: str) -> bool:
    """Validate domain name."""
    if not domain or len(domain) > 253:
        return False
    pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, domain))


def is_valid_indicator(indicator: str, ind_type: str | None = None) -> bool:
    """Validate threat indicator based on type."""
    if not indicator or len(indicator) > 500:
        return False
    indicator = indicator.strip()
    if ind_type in ("IPv4", "IPv6", "ip"):
        return is_valid_ip(indicator)
    elif ind_type in ("domain", "hostname"):
        return is_valid_domain(indicator)
    elif ind_type == "URL":
        return indicator.startswith(("http://", "https://")) and len(indicator) < 2000
    elif ind_type in ("md5", "sha1", "sha256"):
        return bool(re.match(r"^[a-fA-F0-9]{32,64}$", indicator))
    return True  # Unknown type, allow but log


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent XSS."""
    if not text:
        return ""
    # Remove potential script tags and dangerous characters
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)
    text = text[:max_length]
    return text.strip()


def detect_duplicates(threats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate threats, keeping highest score."""
    seen: dict[str, dict] = {}
    for threat in threats:
        indicator = threat.get("indicator", "").strip()
        ind_type = threat.get("type", "unknown")
        key = f"{indicator}:{ind_type}"
        if key not in seen or (threat.get("score", 0) or 0) > (seen[key].get("score", 0) or 0):
            seen[key] = threat
    return list(seen.values())
