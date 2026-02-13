# Network Discovery Tool (NDT)

Een moderne netwerkapparaat-scanner die je thuisnetwerk in kaart brengt met OSINT-integratie.

## Features

- 🔍 **Netwerkscanning**: Automatische detectie van apparaten in je subnet via ICMP pings en ARP-tabel
- 🌐 **Automatische subnet detectie**: Detecteert automatisch het subnet van je actieve netwerkinterface
- 🎯 **MAC-adres identificatie**: Automatische fabrikant-detectie via OUI-database
- 🔐 **Bekende/Onbekende apparaten**: Markeer apparaten als vertrouwd voor toekomstige scans
- 📝 **Device notes**: Voeg notities toe aan specifieke apparaten
- 🔌 **Port scanning**: Scan open poorten op apparaten (optioneel)
- 🔎 **OSINT-integratie** (optioneel): 
  - VirusTotal (reputation, malware detection)
  - AbuseIPDB (abuse confidence)
  - WHOIS/IP-API (geolocation, ISP)
  - IPinfo.io (geolocation)
- 📊 **Modern dashboard**: Real-time overzicht met dark theme, filters en zoekfunctie
- 📈 **Scan geschiedenis**: Houdt historie bij van scans (nieuwe/verdwenen apparaten)
- 🌍 **Multi-language**: Nederlands en Engels
- 📤 **Export**: Download resultaten als JSON of CSV

## Installatie

1. **Clone of download dit project**

2. **Installeer dependencies**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Op macOS/Linux
pip install -r requirements.txt
```

   **Opmerking**: De app gebruikt `subprocess` voor netwerkscanning (geen root vereist). `scapy` staat in requirements.txt maar wordt niet gebruikt.

3. **Configureer OSINT API keys** (optioneel):
```bash
cp osint_config.example.json osint_config.json
# Bewerk osint_config.json en voeg je API keys toe
```

   - **VirusTotal**: Gratis account op https://www.virustotal.com/gui/join-us
   - **AbuseIPDB**: Gratis account op https://www.abuseipdb.com/pricing
   - **IPinfo**: Optioneel (gratis tier werkt zonder key)
   - **WHOIS/IP-API**: Werkt zonder API key

## Gebruik

1. **Start de applicatie**:
```bash
source .venv/bin/activate
python3 app.py
```

2. **Open je browser**:
   - Ga naar `http://localhost:5001`

3. **Voer een scan uit**:
   - Klik op "Scan huidig subnet"
   - Optioneel: vink "OSINT" aan voor uitgebreide intelligence (duurt langer)
   - Optioneel: vink "Ports" aan voor port scanning
   - Bekijk resultaten in de tabel

4. **Apparaten beheren**:
   - Markeer apparaten als "Bekend" of "Onbekend"
   - Voeg notities toe via de 📝 knop
   - Bekijk details via de "Details" knop (toont OSINT data en open poorten)
   - Filter op: Alles, Bekend, Onbekend, Extern, Nieuw
   - Exporteer resultaten via de "Export" dropdown

5. **Taal wijzigen**:
   - Klik op de "Taal" knop rechtsboven
   - Kies tussen Nederlands en English

## Configuratie

### OSINT API Keys

Maak `osint_config.json` aan met je API keys:

```json
{
  "virustotal_api_key": "YOUR_VIRUSTOTAL_API_KEY",
  "abuseipdb_api_key": "YOUR_ABUSEIPDB_API_KEY",
  "ipinfo_api_key": "YOUR_IPINFO_API_KEY_OPTIONAL"
}
```

### Bekende MAC-adressen

Apparaten die je als "Bekend" markeert worden automatisch opgeslagen in `known_macs.json`. Deze worden bij volgende scans automatisch herkend.

### Device Notes

Notities die je toevoegt aan apparaten worden opgeslagen in `device_notes.json`.

### Scan Geschiedenis

De scan geschiedenis wordt opgeslagen in `scan_history.json` en toont nieuwe en verdwenen apparaten per scan.

## Projectstructuur

```
NDT/
├── app.py                 # Flask applicatie
├── scanner/
│   ├── __init__.py
│   ├── network_scan.py    # Netwerk scanning (ping + ARP)
│   ├── mac_lookup.py      # MAC → vendor lookup
│   ├── osint_lookup.py    # OSINT integraties
│   ├── port_scan.py       # Port scanning functionaliteit
│   └── storage.py         # Data opslag
├── templates/
│   └── dashboard.html     # Web interface
├── static/
│   └── style.css          # Styling
├── translations.py        # Taalvertalingen (NL/EN)
├── requirements.txt       # Python dependencies
├── osint_config.json      # OSINT API keys (niet in git)
├── known_macs.json        # Bekende MAC-adressen (niet in git)
├── device_notes.json      # Device notities (niet in git)
└── scan_history.json      # Scan geschiedenis (niet in git)
```

## Technische details

- **Netwerkscanning**: Gebruikt ICMP pings en ARP-tabel (geen root vereist op macOS)
- **Subnet detectie**: Automatische detectie van actieve netwerkinterfaces (en0, en1, eth0, etc.)
- **Performance**: Checkt eerst ARP-cache voor snelle resultaten
- **Port scanning**: Scan van veelgebruikte poorten (22, 80, 443, etc.) met service detectie
- **OSINT**: Rate-limited requests om API-limits te respecteren (0.2s delay tussen requests)
- **Storage**: Eenvoudige JSON-based opslag (kan uitgebreid worden naar SQLite)
- **Sessions**: Flask sessions voor taal- en theme-voorkeuren

## Beperkingen

- Scans werken alleen goed binnen hetzelfde VLAN/broadcast-domein
- Voor andere VLANs moet de scanner in dat VLAN draaien
- OSINT lookups kunnen lang duren bij veel apparaten (rate limiting)
- Port scanning kan langzaam zijn bij veel apparaten
- Automatische subnet detectie werkt alleen op macOS/Linux (gebruikt `ipconfig`/`ifconfig`)

## Licentie

Dit project is gemaakt voor educatieve doeleinden.
