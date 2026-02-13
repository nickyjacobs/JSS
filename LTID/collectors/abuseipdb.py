"""AbuseIPDB threat intelligence collector."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import requests

logger = logging.getLogger(__name__)


class AbuseIPDBCollector:
    """Collects threat data from AbuseIPDB API v2."""

    BASE_URL = "https://api.abuseipdb.com/api/v2"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "Key": api_key,
        }

    def is_configured(self) -> bool:
        """Check if API key is set."""
        return bool(self.api_key)

    def get_blacklist(self, confidence_minimum: int = 90, limit: int = 100) -> list[dict[str, Any]]:
        """Fetch blacklist of most-reported IPs."""
        if not self.is_configured():
            logger.warning("AbuseIPDB: No API key configured")
            return []

        try:
            url = f"{self.BASE_URL}/blacklist"
            params = {
                "confidenceMinimum": confidence_minimum,
                "limit": limit,
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.RequestException as e:
            logger.error("AbuseIPDB blacklist fetch failed: %s", e)
            return []

    def check_ip(self, ip_address: str, max_age_days: int = 90) -> dict[str, Any] | None:
        """Check a single IP address."""
        if not self.is_configured():
            return None

        try:
            url = f"{self.BASE_URL}/check"
            params = {
                "ipAddress": ip_address,
                "maxAgeInDays": max_age_days,
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("data")
        except requests.RequestException as e:
            logger.error("AbuseIPDB check failed for %s: %s", ip_address, e)
            return None

    def get_threat_data(self, limit: int = 100) -> dict[str, Any]:
        """Get aggregated threat data for dashboard."""
        blacklist = self.get_blacklist(confidence_minimum=75, limit=limit)

        # Normalize to common format
        threats = []
        country_counts: dict[str, int] = {}
        total_score = 0

        for item in blacklist:
            ip = item.get("ipAddress", "unknown")
            score = item.get("abuseConfidenceScore", 0)
            country = item.get("countryCode", "XX")
            last_reported = item.get("lastReportedAt", "")

            threats.append({
                "source": "abuseipdb",
                "indicator": ip,
                "type": "ip",
                "score": score,
                "country": country,
                "last_seen": last_reported,
                "raw": item,
            })
            country_counts[country] = country_counts.get(country, 0) + 1
            total_score += score

        return {
            "source": "abuseipdb",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "count": len(threats),
            "threats": threats,
            "metrics": {
                "avg_score": total_score / len(threats) if threats else 0,
                "by_country": country_counts,
                "top_countries": sorted(
                    country_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
            },
        }
