from __future__ import annotations

import json
import os
import time
from ipaddress import ip_address, IPv4Address
from typing import Dict, Optional

import requests

# WHOIS kan via python-whois, maar dat vereist extra dependencies.
# We gebruiken een simpele HTTP-based WHOIS lookup als fallback.


def _is_private_ip(ip: str) -> bool:
    """Check of een IP-adres een private (RFC 1918) adres is."""
    try:
        addr = ip_address(ip)
        return addr.is_private
    except ValueError:
        return False


class OSINTConfigError(Exception):
    """Fout in OSINT-config (ontbrekende API keys)."""


def _config_path() -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "osint_config.json")


def load_osint_config() -> Dict:
    """Laad OSINT API configuratie."""
    path = _config_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def lookup_virustotal_ip(ip: str) -> Optional[Dict]:
    """
    VirusTotal IP lookup.
    Vereist API key in osint_config.json: {"virustotal_api_key": "..."}
    """
    cfg = load_osint_config()
    api_key = cfg.get("virustotal_api_key")
    if not api_key:
        return None

    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": api_key}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            attrs = data.get("data", {}).get("attributes", {})
            
            # Extract relevante info
            last_analysis_stats = attrs.get("last_analysis_stats", {})
            reputation = attrs.get("reputation", 0)
            as_owner = attrs.get("as_owner", "")
            country = attrs.get("country", "")
            
            return {
                "reputation": reputation,
                "harmless": last_analysis_stats.get("harmless", 0),
                "malicious": last_analysis_stats.get("malicious", 0),
                "suspicious": last_analysis_stats.get("suspicious", 0),
                "as_owner": as_owner,
                "country": country,
                "last_analysis_date": attrs.get("last_analysis_date"),
            }
        elif resp.status_code == 404:
            return {"status": "not_found"}
    except Exception as e:
        print(f"[OSINT] VirusTotal error voor {ip}: {e}")
    
    return None


def lookup_whois(ip: str) -> Optional[Dict]:
    """
    WHOIS lookup via ipwhois library of HTTP-based service.
    Gebruikt ip-api.com als gratis alternatief (geen API key nodig).
    """
    try:
        # Check of het een multicast/reserved IP is (geen nuttige WHOIS data)
        addr = ip_address(ip)
        if addr.is_multicast or addr.is_reserved or addr.is_link_local:
            # Stil overslaan - geen nuttige data voor deze IP-types
            return None
        
        # Gebruik ip-api.com (gratis, geen API key nodig, rate limit: 45/min)
        url = f"http://ip-api.com/json/{ip}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                result = {}
                if data.get("country"):
                    result["country"] = data.get("country")
                if data.get("regionName"):
                    result["region"] = data.get("regionName")
                if data.get("city"):
                    result["city"] = data.get("city")
                if data.get("isp"):
                    result["isp"] = data.get("isp")
                if data.get("org"):
                    result["org"] = data.get("org")
                if data.get("as"):
                    result["as"] = data.get("as")
                if data.get("asname"):
                    result["asname"] = data.get("asname")
                if data.get("timezone"):
                    result["timezone"] = data.get("timezone")
                if data.get("lat"):
                    result["lat"] = data.get("lat")
                if data.get("lon"):
                    result["lon"] = data.get("lon")
                
                return result if result else None
            else:
                # IP-API geeft "fail" status voor private ranges en andere speciale IP's
                message = data.get("message", "Unknown")
                # Voor private ranges kunnen we nog steeds lokale info teruggeven
                if "private" in message.lower() and addr.is_private:
                    # Geen externe WHOIS data, maar dat is OK voor private IP's
                    return None
                print(f"[OSINT] WHOIS geen data voor {ip}: {message}")
        else:
            print(f"[OSINT] WHOIS HTTP {resp.status_code} voor {ip}")
    except ValueError:
        # Ongeldig IP formaat
        print(f"[OSINT] WHOIS skip voor {ip} (ongeldig IP formaat)")
    except Exception as e:
        print(f"[OSINT] WHOIS error voor {ip}: {e}")
    
    return None


def lookup_abuseipdb(ip: str) -> Optional[Dict]:
    """
    AbuseIPDB lookup voor IP reputation.
    Vereist API key in osint_config.json: {"abuseipdb_api_key": "..."}
    """
    cfg = load_osint_config()
    api_key = cfg.get("abuseipdb_api_key")
    if not api_key:
        return None

    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": api_key, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": 90, "verbose": ""}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("data", {})
            return {
                "abuse_confidence": result.get("abuseConfidencePercentage", 0),
                "usage_type": result.get("usageType"),
                "is_public": result.get("isPublic"),
                "is_whitelisted": result.get("isWhitelisted"),
                "country": result.get("countryCode"),
                "isp": result.get("isp"),
            }
    except Exception as e:
        print(f"[OSINT] AbuseIPDB error voor {ip}: {e}")
    
    return None


def lookup_ipinfo(ip: str) -> Optional[Dict]:
    """
    IPinfo.io lookup (geolocation, ASN, etc.).
    Werkt zonder API key (gratis tier), maar met key krijg je meer data.
    """
    cfg = load_osint_config()
    api_key = cfg.get("ipinfo_api_key", "")
    
    url = f"https://ipinfo.io/{ip}/json"
    if api_key:
        url += f"?token={api_key}"

    try:
        resp = requests.get(url, timeout=5, headers={"Accept": "application/json"})
        if resp.status_code == 200:
            data = resp.json()
            # IPinfo geeft soms een error message in de response
            if "error" in data:
                print(f"[OSINT] IPinfo error voor {ip}: {data.get('error', {}).get('title', 'Unknown error')}")
                return None
            
            result = {}
            if data.get("city"):
                result["city"] = data.get("city")
            if data.get("region"):
                result["region"] = data.get("region")
            if data.get("country"):
                result["country"] = data.get("country")
            if data.get("org"):
                result["org"] = data.get("org")
            if data.get("timezone"):
                result["timezone"] = data.get("timezone")
            if data.get("loc"):
                result["loc"] = data.get("loc")
            if data.get("hostname"):
                result["hostname"] = data.get("hostname")
            if data.get("postal"):
                result["postal"] = data.get("postal")
            
            # Alleen teruggeven als we daadwerkelijk data hebben
            return result if result else None
        elif resp.status_code == 429:
            print(f"[OSINT] IPinfo rate limit voor {ip} (gebruik API key voor hogere limits)")
        else:
            print(f"[OSINT] IPinfo HTTP {resp.status_code} voor {ip}")
    except Exception as e:
        print(f"[OSINT] IPinfo error voor {ip}: {e}")
    
    return None


def enrich_device_with_osint(device: Dict) -> Dict:
    """
    Verrijk een device-dict met OSINT data van verschillende bronnen.
    Voegt 'osint' key toe met alle verzamelde informatie.
    """
    ip = device.get("ip")
    if not ip:
        return device

    osint_data = {}
    is_private = _is_private_ip(ip)

    # WHOIS / IP-API alleen voor publieke IP's (private ranges geven geen nuttige data)
    # Voor private IP's hebben we al lokale info (hostname, MAC, vendor)
    if not is_private:
        whois_data = lookup_whois(ip)
        if whois_data:
            osint_data["whois"] = whois_data

    # IPinfo alleen voor publieke IP's (geolocation heeft geen zin voor private IP's)
    if not is_private:
        ipinfo_data = lookup_ipinfo(ip)
        if ipinfo_data:
            osint_data["ipinfo"] = ipinfo_data

    # VirusTotal (als API key beschikbaar, werkt voor alle IP's)
    vt_data = lookup_virustotal_ip(ip)
    if vt_data:
        osint_data["virustotal"] = vt_data

    # AbuseIPDB (als API key beschikbaar, werkt voor alle IP's)
    abuse_data = lookup_abuseipdb(ip)
    if abuse_data:
        osint_data["abuseipdb"] = abuse_data

    device["osint"] = osint_data if osint_data else None
    return device
