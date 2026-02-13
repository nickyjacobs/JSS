"""VirusTotal threat intelligence collector (uses requests, avoids vt-py async issues)."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import requests

logger = logging.getLogger(__name__)

VT_API = "https://www.virustotal.com/api/v3"


class VirusTotalCollector:
    """Collects threat data from VirusTotal API v3 via REST."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self._headers = {"x-apikey": api_key} if api_key else {}

    def is_configured(self) -> bool:
        """Check if API key is set."""
        return bool(self.api_key)

    def get_ip_report(self, ip_address: str) -> dict[str, Any] | None:
        """Get VT report for an IP address."""
        if not self.is_configured():
            return None

        try:
            resp = requests.get(
                f"{VT_API}/ip_addresses/{ip_address}",
                headers=self._headers,
                timeout=15,
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json().get("data", {}).get("attributes", {})
            stats = data.get("last_analysis_stats", {}) or {}
            return {
                "ip": ip_address,
                "country": data.get("country", "XX"),
                "as_owner": data.get("as_owner", ""),
                "reputation": data.get("reputation", 0),
                "last_analysis_stats": stats,
                "last_analysis_date": data.get("last_analysis_date", ""),
            }
        except requests.RequestException as e:
            logger.debug("VirusTotal IP lookup failed for %s: %s", ip_address, e)
            return None

    def get_domain_report(self, domain: str) -> dict[str, Any] | None:
        """Get VT report for a domain."""
        if not self.is_configured():
            return None
        try:
            resp = requests.get(
                f"{VT_API}/domains/{domain}",
                headers=self._headers,
                timeout=15,
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json().get("data", {}).get("attributes", {})
            return {
                "domain": domain,
                "reputation": data.get("reputation", 0),
                "last_analysis_stats": data.get("last_analysis_stats", {}) or {},
            }
        except Exception as e:
            logger.debug("VirusTotal domain lookup failed: %s", e)
            return None

    def get_recent_relations(self, limit: int = 50) -> list[dict[str, Any]]:
        """Not supported on free tier."""
        return []

    def get_threat_data(self, sample_ips: list[str] | None = None) -> dict[str, Any]:
        """Get aggregated threat data for dashboard.

        VirusTotal doesn't expose a public feed of recent threats on free tier.
        We check a few known-bad IPs from AbuseIPDB/OTX if provided,
        or return structure for manual checks.
        """
        threats: list[dict[str, Any]] = []
        sample_ips = sample_ips or []

        for ip in sample_ips[:4]:  # VT free: ~4 req/min
            report = self.get_ip_report(ip)
            if report:
                stats = report.get("last_analysis_stats", {}) or {}
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)
                score = malicious * 10 + suspicious * 2

                threats.append({
                    "source": "virustotal",
                    "indicator": ip,
                    "type": "ip",
                    "score": min(score, 100),
                    "country": report.get("country", "XX"),
                    "reputation": report.get("reputation", 0),
                    "malicious": malicious,
                    "suspicious": suspicious,
                    "last_seen": report.get("last_analysis_date", ""),
                    "raw": report,
                })

        return {
            "source": "virustotal",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "count": len(threats),
            "threats": threats,
            "metrics": {
                "checked": len(sample_ips),
                "flagged": len(threats),
            },
        }
