"""Advanced threat intelligence features: correlation and attribution."""
from __future__ import annotations

from typing import Any
from collections import defaultdict
import re


# Known threat actor groups and their indicators
THREAT_ACTORS = {
    "apt28": {
        "names": ["APT28", "Fancy Bear", "Sofacy", "STRONTIUM"],
        "tags": ["apt28", "fancybear", "sofacy"],
        "countries": ["RU"],
        "tlds": [".ru", ".su"],
    },
    "apt29": {
        "names": ["APT29", "Cozy Bear", "The Dukes"],
        "tags": ["apt29", "cozybear", "dukes"],
        "countries": ["RU"],
    },
    "lazarus": {
        "names": ["Lazarus Group", "Hidden Cobra"],
        "tags": ["lazarus", "hiddencobra"],
        "countries": ["KP"],
    },
    "emotet": {
        "names": ["Emotet"],
        "tags": ["emotet", "trickbot"],
        "malware_families": ["emotet", "trickbot"],
    },
    "mirai": {
        "names": ["Mirai Botnet"],
        "tags": ["mirai", "iot", "botnet"],
        "malware_families": ["mirai"],
    },
    "conti": {
        "names": ["Conti Ransomware"],
        "tags": ["conti", "ransomware"],
        "malware_families": ["conti"],
    },
    "lockbit": {
        "names": ["LockBit"],
        "tags": ["lockbit", "ransomware"],
        "malware_families": ["lockbit"],
    },
}


def detect_threat_actor(threat: dict[str, Any]) -> list[str]:
    """
    Detect potential threat actor attribution based on indicators.
    
    Returns list of potential threat actor names.
    """
    actors = []
    indicator = str(threat.get("indicator", "")).lower()
    tags = threat.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    elif not isinstance(tags, list):
        tags = []
    
    tags_lower = [str(t).lower() for t in tags]
    country = threat.get("country", "").upper()
    pulse_name = str(threat.get("pulse_name", "")).lower()
    
    for actor_id, actor_info in THREAT_ACTORS.items():
        # Check tags
        actor_tags = actor_info.get("tags", [])
        if any(tag in tags_lower for tag in actor_tags):
            actors.extend(actor_info["names"])
            continue
        
        # Check country
        actor_countries = actor_info.get("countries", [])
        if country in actor_countries:
            actors.extend(actor_info["names"])
            continue
        
        # Check pulse name
        if any(tag in pulse_name for tag in actor_tags):
            actors.extend(actor_info["names"])
            continue
        
        # Check malware families
        malware_families = actor_info.get("malware_families", [])
        for family in malware_families:
            if family in indicator or family in pulse_name:
                actors.extend(actor_info["names"])
                break
    
    return list(set(actors))  # Remove duplicates


def correlate_threats(threats: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Correlate threats to find relationships.
    
    Groups threats by:
    - Same domain/hostname patterns
    - Same country
    - Same tags
    - Same pulse (OTX)
    - Temporal proximity
    """
    correlations = {
        "by_domain": defaultdict(list),
        "by_country": defaultdict(list),
        "by_tags": defaultdict(list),
        "by_pulse": defaultdict(list),
        "related_groups": [],
    }
    
    # Extract domain patterns
    domain_pattern = re.compile(r'([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}')
    
    for threat in threats:
        indicator = threat.get("indicator", "")
        country = threat.get("country", "XX")
        tags = threat.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        elif not isinstance(tags, list):
            tags = []
        pulse_name = threat.get("pulse_name", "")
        
        # Group by domain pattern
        domains = domain_pattern.findall(indicator)
        if domains:
            base_domain = domains[0][0] if isinstance(domains[0], tuple) else domains[0]
            root_domain = ".".join(base_domain.split(".")[-2:]) if "." in base_domain else base_domain
            correlations["by_domain"][root_domain].append(threat)
        
        # Group by country
        if country and country != "XX":
            correlations["by_country"][country].append(threat)
        
        # Group by tags
        for tag in tags:
            correlations["by_tags"][str(tag)].append(threat)
        
        # Group by pulse
        if pulse_name:
            correlations["by_pulse"][pulse_name].append(threat)
    
    # Find related groups (threats that share multiple attributes)
    threat_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    
    for threat in threats:
        # Create a group key based on multiple attributes
        country = threat.get("country", "XX")
        tags = threat.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        elif not isinstance(tags, list):
            tags = []
        pulse_name = threat.get("pulse_name", "")
        
        # Create group keys
        if tags:
            tag_key = f"tags:{','.join(sorted([str(t).lower() for t in tags[:3]]))}"
            threat_groups[tag_key].append(threat)
        
        if pulse_name:
            pulse_key = f"pulse:{pulse_name}"
            threat_groups[pulse_key].append(threat)
        
        if country and country != "XX":
            country_key = f"country:{country}"
            threat_groups[country_key].append(threat)
    
    # Filter groups with 2+ threats
    correlations["related_groups"] = [
        {
            "key": key,
            "threats": group,
            "count": len(group),
            "indicators": [t.get("indicator") for t in group[:5]],
        }
        for key, group in threat_groups.items()
        if len(group) >= 2
    ]
    
    # Sort by count
    correlations["related_groups"].sort(key=lambda x: x["count"], reverse=True)
    
    return correlations


def improve_country_detection(threat: dict[str, Any]) -> str:
    """
    Improve country detection by checking multiple sources.
    
    Checks:
    - Direct country field
    - Raw data countryCode
    - GeoIP from indicator (if IP)
    - Domain TLD mapping
    - URL domain extraction
    """
    # First check direct country field
    country = threat.get("country", "")
    if country and country != "XX" and len(country) == 2:
        return country.upper()
    
    # Check raw data for country codes
    raw = threat.get("raw", {})
    country = raw.get("countryCode") or raw.get("country") or raw.get("country_code")
    if country and country != "XX" and len(str(country)) == 2:
        return str(country).upper()
    
    # For IP addresses, check AbuseIPDB/VirusTotal country data
    indicator = str(threat.get("indicator", "")).strip()
    threat_type = str(threat.get("type", "")).lower()
    
    # If it's an IP, try to extract country from raw data
    if threat_type in ("ip", "ipv4", "ipv6"):
        # AbuseIPDB stores countryCode in raw
        if raw.get("countryCode"):
            code = str(raw.get("countryCode")).upper()
            if code != "XX" and len(code) == 2:
                return code
        # VirusTotal stores country in raw
        if raw.get("country"):
            code = str(raw.get("country")).upper()
            if code != "XX" and len(code) == 2:
                return code
    
    # For URLs and domains, extract domain and check TLD
    if threat_type in ("url", "domain", "hostname") or indicator.startswith("http"):
        # Extract domain from URL
        domain = indicator
        if "://" in indicator:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(indicator)
                domain = parsed.netloc or parsed.path.split("/")[0]
            except Exception:
                pass
        
        # Extract TLD
        if "." in domain:
            parts = domain.split(".")
            if len(parts) >= 2:
                # Check last two parts for country codes (e.g., .co.uk, .com.au)
                tld2 = ".".join(parts[-2:]).upper()
                tld1 = parts[-1].upper()
                
                # Two-part country TLDs
                country_tlds_2 = {
                    "CO.UK": "GB", "COM.AU": "AU", "COM.BR": "BR",
                    "COM.MX": "MX", "COM.AR": "AR", "CO.ZA": "ZA",
                    "COM.CN": "CN", "CO.JP": "JP", "CO.KR": "KR",
                }
                if tld2 in country_tlds_2:
                    return country_tlds_2[tld2]
                
                # Single-part country TLDs
                country_tlds = {
                    "UK": "GB", "DE": "DE", "FR": "FR", "NL": "NL", "BE": "BE",
                    "IT": "IT", "ES": "ES", "PL": "PL", "SE": "SE",
                    "NO": "NO", "DK": "DK", "FI": "FI", "RU": "RU",
                    "CN": "CN", "JP": "JP", "KR": "KR", "AU": "AU",
                    "CA": "CA", "MX": "MX", "BR": "BR", "AR": "AR",
                    "NZ": "NZ", "ZA": "ZA", "IN": "IN", "SG": "SG",
                    "CH": "CH", "AT": "AT", "IE": "IE", "PT": "PT",
                    "GR": "GR", "CZ": "CZ", "HU": "HU", "RO": "RO",
                }
                if tld1 in country_tlds:
                    return country_tlds[tld1]
    
    return "XX"
