from __future__ import annotations

from typing import Optional

try:
    # Snelste manier: gebruik de manuf-library met ingebouwde OUI-database
    from manuf import manuf  # type: ignore

    _parser = manuf.MacParser()
except Exception:
    _parser = None


def lookup_vendor(mac: str) -> Optional[str]:
    """
    Zoekt de fabrikant op basis van het MAC-adres.

    - Als de `manuf`-library beschikbaar is, gebruiken we die.
    - Anders geven we None terug (vendor onbekend).
    """
    if _parser is None:
        return None

    try:
        vendor = _parser.get_manuf(mac)
        return vendor
    except Exception:
        return None

