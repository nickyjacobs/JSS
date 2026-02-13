"""AlienVault OTX threat intelligence collector."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

try:
    from OTXv2 import OTXv2
    from OTXv2 import IndicatorTypes
except ImportError:
    OTXv2 = None
    IndicatorTypes = None

logger = logging.getLogger(__name__)


class OTXCollector:
    """Collects threat data from AlienVault Open Threat Exchange."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self._client = OTXv2(api_key) if OTXv2 and api_key else None

    def is_configured(self) -> bool:
        """Check if API key and SDK are available."""
        if not self.api_key:
            return False
        if not OTXv2:
            logger.warning("OTX: OTXv2 SDK niet geïnstalleerd. Installeer met: pip install OTXv2")
            return False
        if not self._client:
            return False
        return True

    def get_pulses(self, limit: int = 10) -> list[dict[str, Any]]:
        """Fetch recent pulses (threat intel reports)."""
        if not self.is_configured():
            logger.warning("OTX: No API key or OTXv2 not installed")
            return []

        try:
            pulses = self._client.getall(limit=min(limit, 10), max_page=1, max_items=10)
            return pulses[:limit]
        except Exception as e:
            logger.error("OTX pulses fetch failed: %s", e)
            return []

    def get_pulse_indicators(self, pulse_id: str) -> list[dict[str, Any]]:
        """Get indicators from a specific pulse."""
        if not self.is_configured():
            return []

        try:
            return self._client.get_pulse_indicators(pulse_id)
        except Exception as e:
            logger.error("OTX pulse indicators fetch failed: %s", e)
            return []

    def get_trending(self) -> list[dict[str, Any]]:
        """Fetch trending malware/indicators (uses pulses as proxy)."""
        return self.get_pulses(limit=10)

    def get_threat_data(self, pulse_limit: int = 5) -> dict[str, Any]:
        """Get aggregated threat data for dashboard."""
        pulses = self.get_pulses(limit=pulse_limit)

        threats: list[dict[str, Any]] = []
        type_counts: dict[str, int] = {}
        tag_counts: dict[str, int] = {}

        for pulse in pulses[:5]:
            pulse_id = pulse.get("id", "")
            name = pulse.get("name", "Unknown")
            created = pulse.get("created", "")
            modified = pulse.get("modified", "")
            tags = pulse.get("tags", [])
            indicator_count = pulse.get("indicator_count", 0)

            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Get indicators from pulse
            indicators = self.get_pulse_indicators(pulse_id) if pulse_id else []
            for ind in indicators[:15]:
                ind_type = ind.get("type", "unknown")
                indicator = ind.get("indicator", "")
                type_counts[ind_type] = type_counts.get(ind_type, 0) + 1

                threats.append({
                    "source": "otx",
                    "indicator": indicator,
                    "type": ind_type,
                    "pulse_name": name,
                    "tags": tags,
                    "last_seen": modified or created,
                    "raw": ind,
                })

        return {
            "source": "otx",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "count": len(threats),
            "pulse_count": len(pulses),
            "threats": threats[:200],  # Cap for dashboard
            "metrics": {
                "by_type": type_counts,
                "by_tag": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]),
                "top_types": sorted(
                    type_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
            },
        }
