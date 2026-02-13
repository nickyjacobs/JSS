"""Aggregates threat data from multiple intelligence feeds."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from config import Config
from collectors import AbuseIPDBCollector, OTXCollector, VirusTotalCollector
from lists import ThreatLists
from validators import detect_duplicates, is_valid_indicator
from threat_scoring import calculate_risk_score, get_severity_level, calculate_threat_velocity
from threat_intelligence import detect_threat_actor, correlate_threats, improve_country_detection

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "threat_data.json"


def ensure_data_dir() -> Path:
    """Create data directory if needed."""
    DATA_DIR.mkdir(exist_ok=True)
    return DATA_DIR


class ThreatAggregator:
    """Aggregates and stores threat intelligence from multiple sources."""

    def __init__(self) -> None:
        self.abuseipdb = AbuseIPDBCollector(Config.ABUSEIPDB_API_KEY)
        self.otx = OTXCollector(Config.OTX_API_KEY)
        self.virustotal = VirusTotalCollector(Config.VIRUSTOTAL_API_KEY)
        self.lists = ThreatLists()
        ensure_data_dir()

    def _extract_sample_ips(self, abuse_data: dict, otx_data: dict) -> list[str]:
        """Extract IP indicators for VirusTotal cross-check."""
        ips: set[str] = set()
        for t in abuse_data.get("threats", [])[:5]:
            if t.get("type") == "ip":
                ips.add(t.get("indicator", ""))
        for t in otx_data.get("threats", []):
            if t.get("type") in ("IPv4", "IPv6", "ip"):
                ind = t.get("indicator", "").strip()
                if ind and ("." in ind or ":" in ind):
                    ips.add(ind)
        return list(ips)[:10]

    def fetch_all(self) -> dict[str, Any]:
        """Fetch from all configured sources and aggregate."""
        results: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sources": {},
            "aggregate": {
                "total_threats": 0,
                "by_source": {},
                "by_type": {},
                "by_country": {},
                "top_threats": [],
                "metrics": {},
            },
        }

        # AbuseIPDB (fallback to cache when rate limited)
        try:
            if not self.abuseipdb.is_configured():
                results["sources"]["abuseipdb"] = {"error": "Geen API key geconfigureerd", "count": 0, "threats": []}
            else:
                abuse_data = self.abuseipdb.get_threat_data(limit=100)
                results["sources"]["abuseipdb"] = abuse_data
                results["aggregate"]["by_source"]["abuseipdb"] = abuse_data.get("count", 0)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str:
                prev = self.load()
                if prev and "abuseipdb" in prev.get("sources", {}):
                    ad = prev["sources"]["abuseipdb"]
                    if isinstance(ad, dict) and "threats" in ad:
                        results["sources"]["abuseipdb"] = ad
                        results["aggregate"]["by_source"]["abuseipdb"] = ad.get("count", 0)
                        logger.info("AbuseIPDB: using cached data (rate limited)")
                    else:
                        results["sources"]["abuseipdb"] = {"error": "Rate limit (1000/dag)", "count": 0, "threats": []}
                else:
                    results["sources"]["abuseipdb"] = {"error": "Rate limit (1000/dag)", "count": 0, "threats": []}
            else:
                logger.error("AbuseIPDB fetch failed: %s", e)
                results["sources"]["abuseipdb"] = {"error": err_str[:80], "count": 0, "threats": []}

        # AlienVault OTX
        try:
            if not self.otx.is_configured():
                # Check if API key exists but SDK is missing
                if self.otx.api_key and not self.otx._client:
                    results["sources"]["otx"] = {"error": "OTXv2 SDK niet geïnstalleerd. Installeer met: pip install OTXv2", "count": 0, "threats": []}
                else:
                    results["sources"]["otx"] = {"error": "Geen API key geconfigureerd", "count": 0, "threats": []}
            else:
                otx_data = self.otx.get_threat_data(pulse_limit=5)
                results["sources"]["otx"] = otx_data
                results["aggregate"]["by_source"]["otx"] = otx_data.get("count", 0)
        except Exception as e:
            logger.error("OTX fetch failed: %s", e)
            results["sources"]["otx"] = {"error": str(e)[:80], "count": 0, "threats": []}

        # VirusTotal (cross-check sample IPs from other sources)
        try:
            if not self.virustotal.is_configured():
                results["sources"]["virustotal"] = {"error": "Geen API key geconfigureerd", "count": 0, "threats": []}
            else:
                sample_ips = self._extract_sample_ips(
                    results["sources"].get("abuseipdb", {}),
                    results["sources"].get("otx", {}),
                )
                vt_data = self.virustotal.get_threat_data(sample_ips=sample_ips)
                results["sources"]["virustotal"] = vt_data
                results["aggregate"]["by_source"]["virustotal"] = vt_data.get("count", 0)
        except Exception as e:
            logger.error("VirusTotal fetch failed: %s", e)
            results["sources"]["virustotal"] = {"error": str(e)[:80], "count": 0, "threats": []}

        # Build aggregate
        all_threats: list[dict[str, Any]] = []
        threat_sources: dict[str, list[str]] = {}  # Track all sources per indicator

        for source_name, source_data in results["sources"].items():
            if isinstance(source_data, dict) and "threats" in source_data:
                for t in source_data["threats"]:
                    indicator = t.get("indicator", "").strip()
                    ind_type = t.get("type", "unknown")
                    key = f"{indicator}:{ind_type}"
                    if key not in threat_sources:
                        threat_sources[key] = []
                    if source_name not in threat_sources[key]:
                        threat_sources[key].append(source_name)
                    all_threats.append({**t, "source": source_name})

        # Validate and dedupe threats FIRST
        validated_threats = [
            t for t in all_threats
            if is_valid_indicator(t.get("indicator", ""), t.get("type"))
        ]
        deduped_threats = detect_duplicates(validated_threats)

        # Enhance threats with risk scoring, country detection, and attribution
        enhanced_threats = []
        for t in deduped_threats:
            # Improve country detection
            improved_country = improve_country_detection(t)
            t["country"] = improved_country
            
            # Set sources from our tracking (all sources that reported this indicator)
            indicator = t.get("indicator", "").strip()
            ind_type = t.get("type", "unknown")
            key = f"{indicator}:{ind_type}"
            t["sources"] = threat_sources.get(key, [t.get("source", "unknown")])
            
            # Calculate risk score (uses sources for multi-source bonus)
            risk_score = calculate_risk_score(t)
            t["risk_score"] = round(risk_score, 2)
            t["severity"] = get_severity_level(risk_score)
            
            # Detect threat actor
            actors = detect_threat_actor(t)
            if actors:
                t["threat_actors"] = actors
            
            enhanced_threats.append(t)
        
        # Count types and countries AFTER enhancement
        type_counts: dict[str, int] = {}
        country_counts: dict[str, int] = {}
        severity_counts: dict[str, int] = {}
        
        for t in enhanced_threats:
            ttype = t.get("type", "unknown")
            type_counts[ttype] = type_counts.get(ttype, 0) + 1
            country = t.get("country", "XX")
            if country and country != "XX":
                country_counts[country] = country_counts.get(country, 0) + 1
            severity = t.get("severity", "info")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Correlate threats
        correlations = correlate_threats(enhanced_threats)
        
        # Calculate threat velocity
        velocity_data = calculate_threat_velocity(enhanced_threats)

        # Sort by risk score instead of just score
        sorted_threats = sorted(
            enhanced_threats,
            key=lambda x: (x.get("risk_score") or 0, x.get("score") or 0, x.get("indicator", "")),
            reverse=True,
        )[:100]

        # Apply whitelist/blacklist filtering
        filtered_threats = self.lists.filter_threats(sorted_threats)

        results["aggregate"]["total_threats"] = len(all_threats)
        results["aggregate"]["by_type"] = type_counts
        results["aggregate"]["by_country"] = country_counts
        results["aggregate"]["by_severity"] = severity_counts
        results["aggregate"]["top_threats"] = filtered_threats[:50]
        results["aggregate"]["correlations"] = {
            "related_groups": correlations["related_groups"][:10],
            "by_domain_count": len([k for k, v in correlations["by_domain"].items() if len(v) > 1]),
            "by_country_count": len([k for k, v in correlations["by_country"].items() if len(v) > 1]),
            "by_tags_count": len([k for k, v in correlations["by_tags"].items() if len(v) > 1]),
        }
        results["aggregate"]["velocity"] = velocity_data
        results["aggregate"]["metrics"] = {
            "unique_indicators": len(deduped_threats),
            "top_countries": sorted(
                country_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:20],  # Increased from 10 to 20 for better country coverage
            "top_types": sorted(
                type_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10],
            "severity_distribution": severity_counts,
            "avg_risk_score": round(
                sum(t.get("risk_score", 0) for t in enhanced_threats) / len(enhanced_threats) if enhanced_threats else 0,
                2
            ),
        }

        return results

    def save(self, data: dict[str, Any]) -> None:
        """Persist aggregated data to disk."""
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            logger.error("Failed to save threat data: %s", e)

    def load(self) -> dict[str, Any] | None:
        """Load cached data from disk."""
        try:
            if DATA_FILE.exists():
                with open(DATA_FILE) as f:
                    return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            logger.error("Failed to load threat data: %s", e)
        return None
