# CLI Commands - JacOps Security Suite

Complete command line referentie voor JacOps Security Suite en alle individuele tools.

## Inhoudsopgave

1. [JacOps Security Suite](#jacops-security-suite)
2. [File Type Identifier (FTI)](#file-type-identifier-fti)
3. [Phishing Email Simulator (PES)](#phishing-email-simulator-pes)
4. [Network Device Scanner (NDT)](#network-device-scanner-ndt)
5. [Live Threat Intelligence Dashboard (LTID)](#live-threat-intelligence-dashboard-ltid)
6. [Password Policy Analyzer (PPA)](#password-policy-analyzer-ppa)
7. [Caesar Cipher Frequency Analyzer (CCFA)](#caesar-cipher-frequency-analyzer-ccfa)
8. [DoS Attack Detector (DSAD)](#dos-attack-detector-dsad)
9. [Secure File Sharing System (SFS)](#secure-file-sharing-system-sfs)
10. [Intrusion Detection Monitor (IDM)](#intrusion-detection-monitor-idm)
11. [Web Vulnerability Scanner (WVS)](#web-vulnerability-scanner-wvs)

---

## JacOps Security Suite

### Hoofdmenu Starten

```bash
# Standaard start
python3 jacops.py

# Of maak uitvoerbaar en run direct
chmod +x jacops.py
./jacops.py
```

### Navigatie

- **Tool selecteren**: Kies een nummer (1-10) in het menu
- **Stoppen**: Kies 0 of druk Ctrl+C
- **Terug naar hoofdmenu**: 
  - In CLI tools: Typ 'q' en druk Enter
  - In GUI tools: Druk Ctrl+C

### Geen Command Line Opties

De JacOps Security Suite heeft geen command line argumenten. Alle functionaliteit is beschikbaar via het interactieve menu.

### Poortoverzicht (webinterfaces)

| Tool | Poort | URL |
|------|-------|-----|
| FTI | 8000* | http://localhost:8000 |
| PES | 5000 | http://localhost:5000 |
| NDT | 5001 | http://localhost:5001 |
| LTID | 8001 | http://localhost:8001 |
| PPA | 5500 | http://localhost:5500 |
| CCFA (web) | 8002 | http://localhost:8002 |
| SFS | 8003 | http://localhost:8003 |
| WVS | 8004 | http://localhost:8004 |
| DSAD | 8005 | http://localhost:8005 |
| IDM | 8006 | http://localhost:8006 |

\* FTI probeert 8000–8010; eerste vrije poort. Zie [PORTS.md](PORTS.md) voor details.

---

## File Type Identifier (FTI)

### Via JacOps Security Suite

```bash
python3 jacops.py
# Kies optie [1]
# Kies [1] voor CLI of [2] voor GUI
```

### Direct Gebruik

#### CLI Versie

```bash
cd FTI/src
python3 main.py <bestandspad>
```

**Voorbeelden:**
```bash
# Analyseer een bestand
python3 main.py /path/to/suspicious_file.exe

# Met VirusTotal API key
python3 main.py --vt-api-key YOUR_API_KEY /path/to/file.exe

# Zonder system 'file' command
python3 main.py --no-file-cmd /path/to/file.exe
```

**Opties:**
- `<bestandspad>` - Verplicht: Pad naar het te analyseren bestand
- `--gui` - Start web GUI in plaats van CLI
- `--vt-api-key <key>` - VirusTotal API key (overschrijft config.py)
- `--no-file-cmd` - Gebruik system `file` command niet

**Output:**
- Bestandstype detectie op basis van magic numbers
- File extension verificatie
- MD5 en SHA256 hashes
- Entropy analyse
- VirusTotal scan resultaten (indien API key beschikbaar)
- Mismatch waarschuwingen

#### GUI Versie

```bash
cd FTI/src
python3 main.py --gui
# Of direct:
python3 gui_web.py
```

**Web Interface:**
- Open `http://localhost:8000` in je browser
- Drag & drop of klik om bestand te selecteren
- Maximaal 25MB per bestand
- Export resultaten naar JSON of CSV

**Stoppen:**
- Druk Ctrl+C in de terminal om terug te gaan naar hoofdmenu

---

## Phishing Email Simulator (PES)

### Via JacOps Security Suite

```bash
python3 jacops.py
# Kies optie [2]
```

### Direct Gebruik

```bash
cd PES
python3 app.py
```

**Web Interface:**
- Open `http://localhost:5000` (of de poort die wordt getoond)
- Volledig web dashboard voor phishing campagne management

**Stoppen:**
- Druk Ctrl+C in de terminal

---

## Network Device Scanner (NDT)

### Via JacOps Security Suite

```bash
python3 jacops.py
# Kies optie [3]
```

### Direct Gebruik

```bash
cd NDT
python3 app.py
```

**Web Interface:**
- Open `http://localhost:5001` in je browser
- Klik op "Scan huidig subnet" om te beginnen
- Optioneel: Vink "OSINT" aan voor uitgebreide intelligence
- Optioneel: Vink "Ports" aan voor port scanning

**Features:**
- Automatische subnet detectie
- MAC-adres identificatie
- OSINT integratie (VirusTotal, AbuseIPDB, IPinfo)
- Port scanning
- Device management (bekend/onbekend markeren)
- Export naar JSON/CSV

**Stoppen:**
- Druk Ctrl+C in de terminal

---

## Live Threat Intelligence Dashboard (LTID)

### Via JacOps Security Suite

```bash
python3 jacops.py
# Kies optie [4]
```

### Direct Gebruik

```bash
cd LTID
python3 dashboard.py
```

**Web Dashboard:**
- Open `http://localhost:8001` (of de poort die wordt getoond)
- FastAPI dashboard met WebSocket support
- Real-time threat feeds

**Stoppen:**
- Druk Ctrl+C in de terminal

---

## Password Policy Analyzer (PPA)

### Via JacOps Security Suite

```bash
python3 jacops.py
# Kies optie [5]
# Kies [1] voor CLI of [2] voor GUI
```

### Direct Gebruik

#### CLI Versie (Interactief Menu)

```bash
cd PPA
python3 cli.py
```

Het interactieve menu biedt de volgende opties:
- **[1] Analyseer vanuit JSON bestand** - Laad policy vanuit een JSON bestand
- **[2] Analyseer met handmatige input** - Voer policy parameters handmatig in
- **[3] Export resultaten** - Exporteer analyse resultaten naar JSON
- **[q] Afsluiten** - Terug naar hoofdmenu

#### Command-Line Interface (Voor Scripting)

Voor geautomatiseerd gebruik kan de CLI ook direct worden aangeroepen met command-line argumenten:

```bash
# Analyseer vanuit JSON bestand
python3 cli.py --file example_policy.json

# Analyseer met command-line argumenten
python3 cli.py --min-length 8 --prevent-common-passwords --prevent-user-info

# Exporteer resultaten naar JSON
python3 cli.py --file example_policy.json --export report.json

# Gebruik Engelse taal
python3 cli.py --file example_policy.json --lang en

# Alleen JSON output (voor scripting)
python3 cli.py --file example_policy.json --json
```

**Command-Line Opties:**

**Input opties (één verplicht):**
- `--file, -f <file>` - Pad naar JSON policy bestand
- `--min-length <n>` - Minimale wachtwoordlengte (vereist als geen --file)

**Policy parameters:**
- `--max-length <n>` - Maximale wachtwoordlengte
- `--require-uppercase` - Vereis hoofdletters
- `--require-lowercase` - Vereis kleine letters
- `--require-numbers` - Vereis cijfers
- `--require-special-chars` - Vereis speciale tekens
- `--max-age-days <n>` - Maximale wachtwoord leeftijd (dagen)
- `--min-age-days <n>` - Minimale wachtwoord leeftijd (dagen)
- `--password-history <n>` - Aantal oude wachtwoorden te onthouden
- `--lockout-attempts <n>` - Aantal mislukte pogingen voor lockout
- `--lockout-duration-minutes <n>` - Lockout duur (minuten)
- `--prevent-common-passwords` - Voorkom veelvoorkomende wachtwoorden
- `--prevent-user-info` - Voorkom gebruikersinformatie in wachtwoorden
- `--prevent-repeating-chars` - Voorkom herhalende karakters
- `--prevent-sequential-chars` - Voorkom sequentiële karakters

**Output opties:**
- `--lang {nl,en}` - Taal (standaard: nl)
- `--export, -e <file>` - Exporteer resultaten naar JSON bestand
- `--json` - Alleen JSON output (geen formatted output)
- `--quiet, -q` - Onderdruk gekleurde output

**Voorbeelden:**
```bash
# Volledige policy analyse met command-line argumenten
python3 cli.py \
  --min-length 12 \
  --max-length 128 \
  --require-uppercase \
  --require-lowercase \
  --require-numbers \
  --require-special-chars \
  --password-history 10 \
  --lockout-attempts 5 \
  --lockout-duration-minutes 30 \
  --prevent-common-passwords \
  --prevent-user-info \
  --prevent-repeating-chars \
  --prevent-sequential-chars

# Eenvoudige analyse vanuit bestand
python3 cli.py --file example_policy.json --lang en --export report.json

# Alleen JSON output voor scripting/automation
python3 cli.py --file example_policy.json --json > results.json
```

**Policy JSON Format:**
```json
{
  "min_length": 8,
  "max_length": 128,
  "require_uppercase": true,
  "require_lowercase": true,
  "require_numbers": true,
  "require_special_chars": true,
  "max_age_days": 90,
  "min_age_days": 1,
  "password_history": 5,
  "lockout_attempts": 5,
  "lockout_duration_minutes": 30,
  "prevent_common_passwords": true,
  "prevent_user_info": true,
  "prevent_repeating_chars": true,
  "prevent_sequential_chars": true
}
```

#### GUI Versie

```bash
cd PPA
python3 app.py
```

**Web Interface:**
- Open `http://localhost:5000` (of de poort die wordt getoond)
- Upload of voer policy in via web interface
- Visuele rapporten en scoring

**Stoppen:**
- Druk Ctrl+C in de terminal

---

## Caesar Cipher Frequency Analyzer (CCFA)

### Via JacOps Security Suite

```bash
python3 jacops.py
# Kies optie [6]
# Kies [1] voor CLI of [2] voor GUI
```

### Direct Gebruik

#### CLI Versie

```bash
cd CCFA
python3 caesar_decoder.py
```

**Interactieve Mode:**
- Voer gecodeerde tekst in
- Tool detecteert automatisch de shift
- Toont alle mogelijke decoderingen
- Kies de juiste decodering

**Voorbeelden:**
```bash
# Start interactieve decoder
python3 caesar_decoder.py

# Voer gecodeerde tekst in wanneer gevraagd
# Tool toont alle 26 mogelijke shifts
# Kies de juiste decodering
```

#### GUI Versie

```bash
cd CCFA
python3 caesar_gui.py
```

**Tkinter GUI:**
- Grafische interface voor Caesar cipher decodering
- Real-time frequency analysis
- Visuele weergave van shifts

**Stoppen:**
- Sluit het GUI venster of druk Ctrl+C

---

## DoS Attack Detector (DSAD)

### Overzicht

De DoS Attack Detector monitort netwerkverkeer in real-time om Denial of Service aanvallen te detecteren. Het analyseert verschillende soorten flood attacks zoals SYN floods, UDP floods, ICMP floods en HTTP floods.

### CLI Gebruik

Start de CLI via het hoofdmenu van JacOps Security Suite:

```bash
python3 jacops.py
# Kies optie 7 (DoS Attack Detector)
# Kies optie 1 (CLI versie)
```

**Interactief Menu:**

1. **Start monitoring (met configuratie)**: Configureer alle instellingen handmatig
   - Network interface selectie
   - Thresholds voor verschillende attack types
   - Time window instellingen

2. **Start monitoring (standaard instellingen)**: Start met default thresholds
   - SYN Flood: 100 packets per time window
   - UDP Flood: 200 packets per time window
   - ICMP Flood: 150 packets per time window
   - HTTP Flood: 300 requests per time window
   - Time Window: 10 seconden

3. **DoS test (simulatie)**: Voer een lokale test uit om de detector te verifiëren
   - Start monitoring op loopback (127.0.0.1)
   - Kies type: SYN, UDP, ICMP of alle types
   - Genereert gesimuleerd testverkeer dat de detector moet oppikken
   - Alleen voor lokaal testen; vereist root/sudo

**Monitoring Process:**

- De detector monitort continu netwerkverkeer
- Alerts worden getoond wanneer thresholds worden overschreden
- Druk Ctrl+C om te stoppen

**Detecteerde Attack Types:**

- **SYN Flood**: Detecteert half-open TCP verbindingen
- **UDP Flood**: Detecteert UDP packet floods
- **ICMP Flood**: Detecteert ICMP packet floods (ping floods)
- **HTTP Flood**: Detecteert HTTP request floods

**Alert Informatie:**

Wanneer een attack wordt gedetecteerd, zie je:
- Attack type
- Source IP adres
- Packet count (en threshold)
- Attack rate (packets per seconde)
- Timestamp

### GUI Gebruik

Start de GUI via het hoofdmenu:

```bash
python3 jacops.py
# Kies optie 7 (DoS Attack Detector)
# Kies optie 2 (GUI versie)
```

De web interface opent automatisch in je browser op `http://localhost:8005`

**Web Interface Features:**

- **Control Panel**: Start/stop monitoring, selecteer network interface
- **Configuration**: Pas thresholds en time window aan
- **Real-time Statistics**: Live monitoring van packet counts met progress bars
- **Attack Alerts**: Real-time alerts wanneer attacks worden gedetecteerd
- **Visual Feedback**: Color-coded progress bars (green → yellow → red)

**Gebruik via Web:**

1. Selecteer network interface (of "All Interfaces")
2. Pas thresholds aan indien nodig
3. Klik "Start Monitoring"
4. Bekijk real-time statistics en alerts

### Configuratie

Bewerk `DSAD/config.py` of maak `.env` bestand aan:

```env
DSAD_HOST=127.0.0.1
DSAD_PORT=8005
DSAD_SYN_THRESHOLD=100
DSAD_UDP_THRESHOLD=200
DSAD_ICMP_THRESHOLD=150
DSAD_HTTP_THRESHOLD=300
DSAD_TIME_WINDOW=10
```

### Vereisten

- **scapy**: Voor packet capture
- **flask**: Voor web interface
- **flask-cors**: Voor CORS support
- **python-dotenv**: Voor configuratie
- **netifaces**: Voor network interface detectie (optioneel)

Installatie:

```bash
cd DSAD
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# of
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### DoS Test Script (simulatie)

Voor handmatig testen of integratie in scripts:

```bash
cd DSAD
# Vereist root voor raw packets
sudo python3 dos_test.py --type syn --target 127.0.0.1 --count 150 --duration 8
```

**Opties:**

| Optie | Beschrijving | Default |
|-------|--------------|---------|
| `--type`, `-t` | Type: `syn`, `udp`, `icmp`, `all` | syn |
| `--target` | Doel-IP (alleen lokaal aanbevolen) | 127.0.0.1 |
| `--count`, `-c` | Aantal pakketten per type | 150 |
| `--duration`, `-d` | Duur in seconden | 8 |
| `--interface`, `-i` | Netwerkinterface (optioneel) | - |

Start de detector (optie 1 of 2) op interface **lo** (loopback) of "Alle" voordat je het testscript in een ander terminalvenster uitvoert, om de alerts te zien.

### Beveiliging & Permissions

⚠️ **BELANGRIJK**: 
- Packet capture vereist meestal root/administrator rechten
- Gebruik alleen op netwerken waar je toestemming hebt
- Monitor alleen je eigen netwerkverkeer of met expliciete toestemming
- De DoS-test stuurt alleen naar 127.0.0.1; gebruik nooit tegen externe doelen zonder toestemming
- DoS detection kan false positives geven bij normale high-traffic situaties

**Linux/Mac:**
```bash
sudo python3 jacops.py  # Of gebruik capabilities
```

**Windows:**
- Run als Administrator
- Mogelijk extra drivers nodig voor packet capture

### Technische Details

- **Packet Capture**: Gebruikt scapy voor low-level packet analysis
- **Time Windows**: Sliding window algoritme voor rate calculation
- **Alert Cooldown**: 5 seconden tussen alerts voorzelfde attack type/IP
- **Threading**: Statistics updates in separate thread voor GUI
- **Real-time Updates**: Web interface pollt elke 500ms voor updates

### Via JacOps Security Suite

```bash
python3 jacops.py
# Kies optie [7]
# Kies [1] voor CLI of [2] voor GUI
```

### Direct Gebruik

#### CLI Versie

```bash
cd DSAD
python3 dos_detector.py [opties]
```

**Voorbeelden:**
```bash
# Standaard monitoring
python3 dos_detector.py

# Met aangepaste threshold
python3 dos_detector.py --threshold 1000

# Specifieke interface
python3 dos_detector.py --interface eth0

# Met alert interval
python3 dos_detector.py --alert-interval 60
```

**Opties:**
- `--interface <iface>` - Netwerk interface om te monitoren (standaard: auto-detect)
- `--threshold <num>` - Aantal pakketten per seconde voor alert (standaard: 500)
- `--alert-interval <sec>` - Tijd tussen alerts in seconden (standaard: 30)
- `--verbose` - Uitgebreide output

**Output:**
- Real-time packet count
- Alerts bij threshold overschrijding
- Statistieken per IP adres

#### GUI Versie

```bash
cd DSAD
python3 dos_detector_gui.py
```

**Tkinter GUI:**
- Real-time monitoring dashboard
- Visuele weergave van netwerkverkeer
- Configureerbare thresholds
- Alert notificaties

**Stoppen:**
- Sluit het GUI venster of druk Ctrl+C

---

## Secure File Sharing System (SFS)

Het Secure File Sharing System biedt veilige bestandsdeling met encryptie, tijdsgebonden toegang en wachtwoordbescherming.

### Via jacops.py (Aanbevolen)

```bash
python3 jacops.py
# Kies [8] Secure File Sharing System
# Kies [1] voor CLI of [2] voor GUI
```

### CLI Versie

```bash
cd SFS
python3 cli.py
```

**Interactief Menu:**
- `[1]` Upload bestand - Upload een bestand met optionele wachtwoordbescherming
- `[2]` Download bestand - Download een bestand met token en wachtwoord
- `[3]` Lijst actieve bestanden - Toon alle actieve bestanden met tokens
- `[4]` Verwijder bestand - Verwijder een bestand met token
- `[5]` Ruim verlopen bestanden op - Verwijder alle verlopen bestanden
- `[q]` Afsluiten - Terug naar hoofdmenu

**Upload Proces:**
1. Kies optie `[1]`
2. Voer pad naar bestand in
3. Optioneel: Voer wachtwoord in (Enter voor geen wachtwoord)
4. Voer verlooptijd in uren in (standaard: 24)
5. Ontvang token voor delen

**Download Proces:**
1. Kies optie `[2]`
2. Voer token in
3. Voer wachtwoord in (indien vereist)
4. Geef opslaglocatie op
5. Bestand wordt gedownload en ontsleuteld

**Voorbeelden:**
```bash
# Upload een bestand
python3 cli.py
# Kies [1]
# Voer pad in: /path/to/file.pdf
# Wachtwoord: (optioneel)
# Verlooptijd: 48
# Ontvang token

# Download een bestand
python3 cli.py
# Kies [2]
# Voer token in: abc123...
# Wachtwoord: (indien vereist)
# Opslaan als: downloaded_file.pdf
```

### GUI Versie

```bash
cd SFS
python3 app.py
```

Open vervolgens je browser naar `http://localhost:8003`

**Web Interface Features:**
- **Upload**: Drag & drop of klik om bestand te selecteren
- **Bestandslijst**: Toon alle actieve bestanden met details
- **Download**: Download via token met wachtwoord (indien vereist)
- **Verwijder**: Verwijder bestanden direct vanuit de interface

**Upload via Web:**
1. Sleep bestand naar upload gebied of klik om te selecteren
2. Optioneel: Voer wachtwoord in
3. Stel verlooptijd in (uren)
4. Klik "Upload Bestand"
5. Kopieer token voor delen

**Download via Web:**
1. Voer token in
2. Voer wachtwoord in (indien vereist)
3. Klik "Download Bestand"
4. Bestand wordt automatisch gedownload

### Configuratie

Bewerk `SFS/config.py` of maak `.env` bestand aan:

```env
SFS_HOST=127.0.0.1
SFS_PORT=8003
SFS_MAX_FILE_SIZE=100  # In MB
SFS_TOKEN_LENGTH=32
SFS_DEFAULT_EXPIRY=24  # In uren
```

### Beveiliging

- **Encryptie**: Alle bestanden worden versleuteld met Fernet (AES-128)
- **Token generatie**: Cryptografisch veilige tokens
- **Wachtwoordbescherming**: Optionele SHA-256 hashing
- **Automatische cleanup**: Verlopen bestanden worden automatisch verwijderd
- **File size limits**: Configureerbare maximale bestandsgrootte (standaard: 100MB)

### Bestandsopslag

Bestanden worden opgeslagen in:
- `SFS/storage/uploads/` - Versleutelde bestanden (.enc)
- `SFS/storage/metadata/` - Bestandsmetadata (JSON)

**Belangrijk:** De `storage/` directory bevat gevoelige data. Zorg voor goede backups en beveiliging.

---

## Algemene Tips

### Tab Completion

In de File Type Identifier CLI tool is tab completion beschikbaar voor file paths:
- Typ een deel van het pad
- Druk TAB voor automatische aanvulling
- Werkt met relatieve en absolute paths

### Terug naar Hoofdmenu

- **CLI tools**: Typ 'q' en druk Enter
- **GUI tools**: Druk Ctrl+C in de terminal

### Applicatie Stoppen

- **In hoofdmenu**: Kies 0 of druk Ctrl+C
- **In GUI tools**: Druk Ctrl+C om terug te gaan naar hoofdmenu, dan 0 of Ctrl+C om te stoppen

### Logging en Debugging

De meeste tools ondersteunen verbose mode voor debugging:
- Voeg `-v` of `--verbose` toe aan commands waar beschikbaar
- Check individuele tool README's voor specifieke logging opties

---

## Troubleshooting

### Port Conflicts

De volgende poorten worden gebruikt door de web interfaces:

- **PES**: 5000 | **NDT**: 5001 | **LTID**: 8001 | **PPA**: 5500 | **CCFA**: 8002
- **SFS**: 8003 | **WVS**: 8004 | **DSAD**: 8005 | **IDM**: 8006
- **FTI GUI**: Eerste vrije poort in 8000–8010

Als een poort al in gebruik is, pas dan de configuratie aan in het respectievelijke `config.py` of via `.env` (zie [PORTS.md](PORTS.md)).

### Dependencies

Als een tool niet start:
1. Check of alle dependencies geïnstalleerd zijn: `pip install -r requirements.txt`
2. Check de tool-specifieke README voor extra requirements
3. Check Python versie: `python3 --version` (moet 3.7+ zijn)

### Permissions

Sommige tools vereisen specifieke permissions:
- **NDT**: Netwerk scanning vereist mogelijk root of speciale netwerk permissions
- **DSAD**: Packet capture vereist mogelijk root of speciale permissions

---

## Voorbeelden Combinaties

### Workflow: Bestand Analyseren

```bash
# Start JacOps Security Suite
python3 jacops.py

# Kies [1] voor File Type Identifier
# Kies [1] voor CLI
# Typ bestandspad (met TAB completion)
# Bekijk resultaten
# Typ 'q' om terug te gaan
```

### Workflow: Netwerk Scannen

```bash
# Start JacOps Security Suite
python3 jacops.py

# Kies [3] voor Network Device Scanner
# Web interface opent automatisch
# Voer scan uit in browser
# Druk Ctrl+C om terug te gaan
```

---

## Intrusion Detection Monitor (IDM)

De Intrusion Detection Monitor houdt auth-log in de gaten en signaleert mislukte logins (brute-force).

### Via jacops.py (Aanbevolen)

```bash
python3 jacops.py
# Kies [9] Intrusion Detection Monitor
# Kies [1] voor CLI of [2] voor GUI
```

### CLI Versie

```bash
cd IDM
python3 cli.py
```

**Menu:**
- `[1]` Start monitoring (auth.log)
- `[2]` Configuratie (logpad, drempel, tijdvenster)
- `[q]` Afsluiten

**Configuratie:** Logpad (bijv. `/var/log/auth.log`), drempel mislukte logins, tijdvenster in seconden. Voor `/var/log/auth.log` is vaak `sudo` nodig.

**Stoppen:** Ctrl+C stopt monitoring en keert terug naar het menu.

### GUI Versie

```bash
cd IDM
python3 app.py
```

Open `http://localhost:8006`

**Web Interface:**
- Start/Stop monitoring
- Configuratie: logpad, drempel, tijdvenster (alleen wijzigbaar als monitoring gestopt is)
- Real-time intrusion alerts

**Dependencies:** `cd IDM && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

---

## Web Vulnerability Scanner (WVS)

Het Web Vulnerability Scanner scant websites op veelvoorkomende beveiligingskwetsbaarheden zoals SQL injection, XSS, directory traversal en meer.

### Via jacops.py (Aanbevolen)

```bash
python3 jacops.py
# Kies [10] Web Vulnerability Scanner
# Kies [1] voor CLI of [2] voor GUI
```

### CLI Versie

```bash
cd WVS
python3 cli.py
```

**Interactief Menu:**
- `[1]` Scan website - Scan een website op kwetsbaarheden
- `[q]` Afsluiten - Terug naar hoofdmenu

**Scan Proces:**
1. Kies optie `[1]`
2. Voer URL in om te scannen (bijv. `https://example.com`)
3. Selecteer scan types:
   - `[1]` Alle scans (standaard)
   - `[2]` SQL Injection
   - `[3]` XSS (Cross-Site Scripting)
   - `[4]` Directory Traversal
   - `[5]` Command Injection
   - `[6]` File Upload
4. Bekijk scan resultaten met severity levels

**Voorbeelden:**
```bash
# Scan een website
python3 cli.py
# Kies [1]
# Voer URL in: https://example.com
# Selecteer scan types: 1 (alle scans)
# Bekijk resultaten
```

### GUI Versie

```bash
cd WVS
python3 app.py
```

Open vervolgens je browser naar `http://localhost:8004`

**Web Interface Features:**
- **URL Invoer**: Voer website URL in
- **Scan Type Selectie**: Kies welke scans je wilt uitvoeren
- **Real-time Resultaten**: Bekijk resultaten tijdens scan
- **Severity Coding**: Kwetsbaarheden gecodeerd op severity (Critical, High, Medium, Low)
- **Gedetailleerde Rapportage**: Uitgebreide informatie per kwetsbaarheid

**Scan via Web:**
1. Voer website URL in
2. Selecteer scan types (of kies "Alle scans")
3. Klik "Start Scan"
4. Bekijk resultaten met severity summary en details

### Gedetecteerde Kwetsbaarheden

- **SQL Injection**: Detecteert SQL foutmeldingen en injection mogelijkheden
- **XSS**: Vindt Cross-Site Scripting kwetsbaarheden
- **Directory Traversal**: Test op path traversal kwetsbaarheden
- **Command Injection**: Detecteert command execution mogelijkheden
- **File Upload**: Controleert file upload formulieren op beveiligingsproblemen

### Configuratie

Bewerk `WVS/config.py` of maak `.env` bestand aan:

```env
WVS_HOST=127.0.0.1
WVS_PORT=8004
WVS_TIMEOUT=10
WVS_ENABLE_SQL=true
WVS_ENABLE_XSS=true
```

### Beveiliging

⚠️ **BELANGRIJK**: 
- Gebruik alleen op websites waar je toestemming hebt
- Ongeautoriseerd scannen is illegaal
- Gebruik alleen voor security testing van je eigen applicaties

---

Voor meer gedetailleerde informatie, zie de individuele tool README's in de respectievelijke directories.
