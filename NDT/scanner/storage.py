from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set

# Eenvoudige opslag met JSON-persistentie voor bekende MAC-adressen

_last_scan_timestamp: Optional[datetime] = None
_last_scan_devices: List[Dict] = []
_last_selected_network: Optional[str] = None

_KNOWN_MACS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "known_macs.json"
)
_NOTES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "device_notes.json"
)
_HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scan_history.json"
)


def _load_known_macs() -> Set[str]:
    """Laad bekende MAC-adressen uit JSON-bestand."""
    if not os.path.exists(_KNOWN_MACS_FILE):
        return set()
    try:
        with open(_KNOWN_MACS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("macs", []))
    except Exception:
        return set()


def _save_known_macs(macs: Set[str]) -> None:
    """Bewaar bekende MAC-adressen naar JSON-bestand."""
    try:
        with open(_KNOWN_MACS_FILE, "w", encoding="utf-8") as f:
            json.dump({"macs": list(macs)}, f, indent=2)
    except Exception:
        pass


def mark_as_known(mac: str) -> None:
    """Markeer een MAC-adres als bekend."""
    if not mac:
        return
    macs = _load_known_macs()
    macs.add(mac.lower())
    _save_known_macs(macs)


def mark_as_unknown(mac: str) -> None:
    """Markeer een MAC-adres als onbekend."""
    if not mac:
        return
    macs = _load_known_macs()
    macs.discard(mac.lower())
    _save_known_macs(macs)


def get_known_macs() -> Set[str]:
    """Geef alle bekende MAC-adressen terug."""
    return _load_known_macs()


def save_scan(devices: List[Dict], selected_network: str) -> None:
    global _last_scan_timestamp, _last_scan_devices, _last_selected_network
    _last_scan_timestamp = datetime.utcnow()
    
    # Markeer devices als bekend op basis van opgeslagen MAC-adressen
    known_macs = get_known_macs()
    for d in devices:
        mac_raw = d.get("mac")
        mac = mac_raw.lower() if mac_raw else ""
        d["known"] = mac in known_macs if mac else False
    
    _last_scan_devices = devices
    _last_selected_network = selected_network


def get_latest_scan() -> Tuple[Optional[datetime], List[Dict], Optional[str]]:
    return _last_scan_timestamp, _last_scan_devices, _last_selected_network


def _load_notes() -> Dict[str, str]:
    """Laad device notities (keyed by MAC)."""
    if not os.path.exists(_NOTES_FILE):
        return {}
    try:
        with open(_NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_notes(notes: Dict[str, str]) -> None:
    """Bewaar device notities."""
    try:
        with open(_NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2)
    except Exception:
        pass


def get_note(mac: str) -> Optional[str]:
    """Haal notitie op voor een MAC-adres."""
    notes = _load_notes()
    return notes.get(mac.lower())


def set_note(mac: str, note: str) -> None:
    """Zet notitie voor een MAC-adres."""
    notes = _load_notes()
    mac_lower = mac.lower()
    if note.strip():
        notes[mac_lower] = note.strip()
    else:
        notes.pop(mac_lower, None)
    _save_notes(notes)


def _load_history() -> List[Dict]:
    """Laad scan geschiedenis."""
    if not os.path.exists(_HISTORY_FILE):
        return []
    try:
        with open(_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_history(history: List[Dict]) -> None:
    """Bewaar scan geschiedenis (behoud laatste 50 scans)."""
    try:
        # Behouden alleen laatste 50 scans
        history = history[-50:]
        with open(_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, default=str)
    except Exception:
        pass


def save_scan_with_history(devices: List[Dict], selected_network: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Sla scan op en vergelijk met vorige scan.
    Retourneert (new_devices, removed_devices).
    """
    global _last_scan_timestamp, _last_scan_devices, _last_selected_network
    
    # Laad notities en voeg toe aan devices
    notes = _load_notes()
    known_macs = get_known_macs()
    
    # Markeer devices als bekend en voeg notities toe
    for d in devices:
        mac_raw = d.get("mac")
        mac = mac_raw.lower() if mac_raw else ""
        d["known"] = mac in known_macs if mac else False
        d["note"] = notes.get(mac, "") if mac else ""
        d["first_seen"] = _last_scan_timestamp  # Voor nu, later uit history halen
    
    # Vergelijk met vorige scan (als die bestaat)
    # Helper functie om MAC veilig te krijgen
    def safe_get_mac(device):
        mac = device.get("mac")
        return mac.lower() if mac else None
    
    previous_macs = {safe_get_mac(d) for d in _last_scan_devices if safe_get_mac(d)} if _last_scan_devices else set()
    current_macs = {safe_get_mac(d) for d in devices if safe_get_mac(d)}
    
    new_macs = current_macs - previous_macs
    removed_macs = previous_macs - current_macs
    
    new_devices = [d for d in devices if safe_get_mac(d) in new_macs]
    removed_devices = [d for d in _last_scan_devices if safe_get_mac(d) in removed_macs] if _last_scan_devices else []
    
    # Markeer nieuwe devices (alle devices bij eerste scan zijn "nieuw")
    if not _last_scan_devices:
        # Eerste scan: markeer alles als nieuw
        for d in devices:
            d["is_new"] = True
    else:
        # Volgende scans: alleen echt nieuwe devices
        for d in devices:
            mac = safe_get_mac(d)
            if mac and mac in new_macs:
                d["is_new"] = True
            else:
                d["is_new"] = False
    
    # Sla geschiedenis op
    history = _load_history()
    history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "device_count": len(devices),
        "new_count": len(new_devices),
        "removed_count": len(removed_devices),
    })
    _save_history(history)
    
    _last_scan_timestamp = datetime.utcnow()
    _last_scan_devices = devices
    _last_selected_network = selected_network
    
    return new_devices, removed_devices


def get_scan_history() -> List[Dict]:
    """Haal scan geschiedenis op."""
    return _load_history()

