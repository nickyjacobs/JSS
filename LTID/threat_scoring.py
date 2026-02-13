"""Threat scoring and risk calculation module."""
from __future__ import annotations

from typing import Any
from datetime import datetime, timezone


def calculate_risk_score(threat: dict[str, Any]) -> float:
    """
    Calculate comprehensive risk score (0-100) for a threat indicator.
    
    Factors considered:
    - Source reliability (AbuseIPDB=high, OTX=medium, VirusTotal=high)
    - Individual source scores
    - Number of sources reporting the threat
    - Recency (more recent = higher score)
    - Threat type severity
    - Country risk (if available)
    """
    score = 0.0
    sources = threat.get("sources", [])
    if isinstance(sources, str):
        sources = [sources]
    elif not isinstance(sources, list):
        sources = [threat.get("source", "unknown")]
    
    # Base score from individual sources
    base_score = threat.get("score", 0) or 0
    if isinstance(base_score, (int, float)):
        score += min(base_score, 50)  # Cap at 50 for base score
    
    # Source reliability multiplier
    source_weights = {
        "abuseipdb": 1.2,  # High reliability
        "virustotal": 1.3,  # Very high reliability
        "otx": 1.0,  # Medium reliability
    }
    
    source_multiplier = 1.0
    for src in sources:
        src_lower = src.lower() if isinstance(src, str) else "unknown"
        weight = source_weights.get(src_lower, 0.8)
        source_multiplier = max(source_multiplier, weight)
    
    score *= source_multiplier
    
    # Multiple sources bonus (if threat appears in multiple feeds)
    if len(sources) > 1:
        score += min(len(sources) * 10, 30)  # Up to 30 points for multi-source
    
    # Recency bonus (more recent = higher score)
    last_seen = threat.get("last_seen", "")
    if last_seen:
        try:
            # Try parsing ISO format
            if "T" in str(last_seen):
                dt = datetime.fromisoformat(str(last_seen).replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(str(last_seen), "%Y-%m-%d %H:%M:%S")
            
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            age_hours = (now - dt).total_seconds() / 3600
            
            # Recent threats get bonus (within 24h = +15, within 7d = +10, within 30d = +5)
            if age_hours < 24:
                score += 15
            elif age_hours < 168:  # 7 days
                score += 10
            elif age_hours < 720:  # 30 days
                score += 5
        except (ValueError, TypeError):
            pass
    
    # Threat type severity
    threat_type = str(threat.get("type", "")).lower()
    type_severity = {
        "ip": 1.0,
        "ipv4": 1.0,
        "ipv6": 1.0,
        "hostname": 1.1,
        "domain": 1.2,
        "url": 1.3,
        "filehash-md5": 1.4,
        "filehash-sha1": 1.4,
        "filehash-sha256": 1.5,
    }
    type_multiplier = type_severity.get(threat_type, 1.0)
    score *= type_multiplier
    
    # VirusTotal specific bonuses
    if "virustotal" in [s.lower() for s in sources]:
        malicious = threat.get("malicious", 0) or threat.get("raw", {}).get("last_analysis_stats", {}).get("malicious", 0) or 0
        suspicious = threat.get("suspicious", 0) or threat.get("raw", {}).get("last_analysis_stats", {}).get("suspicious", 0) or 0
        if malicious > 0:
            score += min(malicious * 2, 20)  # Up to 20 points
        if suspicious > 0:
            score += min(suspicious, 10)  # Up to 10 points
    
    # OTX tags bonus (certain tags indicate higher severity)
    tags = threat.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    elif not isinstance(tags, list):
        tags = []
    
    high_severity_tags = ["malware", "c2", "botnet", "ransomware", "trojan", "backdoor", "rat"]
    for tag in tags:
        if any(severity_tag in str(tag).lower() for severity_tag in high_severity_tags):
            score += 5
    
    # Cap final score between 0 and 100
    return min(max(score, 0), 100)


def get_severity_level(risk_score: float) -> str:
    """Convert risk score to severity level."""
    if risk_score >= 75:
        return "critical"
    elif risk_score >= 50:
        return "high"
    elif risk_score >= 25:
        return "medium"
    elif risk_score > 0:
        return "low"
    else:
        return "info"


def calculate_threat_velocity(threats_history: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calculate threat velocity metrics.
    
    Returns:
        - threats_per_hour: Average threats per hour
        - peak_hour: Hour with most threats
        - trend: "increasing", "decreasing", or "stable"
    """
    if not threats_history:
        return {
            "threats_per_hour": 0,
            "peak_hour": None,
            "trend": "stable",
            "velocity_score": 0,
        }
    
    # Group by hour
    hourly_counts: dict[int, int] = {}
    for threat in threats_history:
        last_seen = threat.get("last_seen", "")
        if last_seen:
            try:
                if "T" in str(last_seen):
                    dt = datetime.fromisoformat(str(last_seen).replace("Z", "+00:00"))
                else:
                    dt = datetime.strptime(str(last_seen), "%Y-%m-%d %H:%M:%S")
                hour = dt.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            except (ValueError, TypeError):
                pass
    
    if not hourly_counts:
        return {
            "threats_per_hour": 0,
            "peak_hour": None,
            "trend": "stable",
            "velocity_score": 0,
        }
    
    total_threats = sum(hourly_counts.values())
    hours_span = len(hourly_counts) or 1
    threats_per_hour = total_threats / hours_span
    
    peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None
    
    # Simple trend calculation (comparing first half vs second half)
    sorted_hours = sorted(hourly_counts.keys())
    if len(sorted_hours) > 1:
        mid = len(sorted_hours) // 2
        first_half = sum(hourly_counts[h] for h in sorted_hours[:mid])
        second_half = sum(hourly_counts[h] for h in sorted_hours[mid:])
        
        if second_half > first_half * 1.2:
            trend = "increasing"
        elif first_half > second_half * 1.2:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    # Velocity score (0-100) based on threats per hour
    velocity_score = min(threats_per_hour * 10, 100)
    
    return {
        "threats_per_hour": round(threats_per_hour, 2),
        "peak_hour": peak_hour,
        "trend": trend,
        "velocity_score": round(velocity_score, 2),
        "hourly_distribution": hourly_counts,
    }
