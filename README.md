# JacOps Security Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Een uitgebreide cybersecurity multitool suite met 10 professionele security tools. Alle tools zijn toegankelijk via een centraal interactief menu (CLI en/of web-GUI).

## Overzicht

- **Eén menu** – Start `python3 jacops.py` en kies een tool (1–10).
- **CLI en GUI** – Veel tools bieden zowel command-line als webinterface.
- **Geen poortconflicten** – Elke tool heeft een vaste poort; zie [PORTS.md](PORTS.md).

## Installatie

1. **Clone de repository**
   ```bash
   git clone https://github.com/JOUW-USERNAME/jacops-security-suite.git
   cd jacops-security-suite
   ```
   *(Vervang `JOUW-USERNAME` door je GitHub-gebruikersnaam of de organisatie.)*

2. **Python 3.9+**
   ```bash
   python3 --version
   ```

3. **Dependencies per tool**
   - Elke tool heeft een eigen `requirements.txt` in zijn directory.
   - Voor web-GUI tools: `cd TOOLNAAM && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
   - Optioneel: kopieer `.env.example` naar `.env` in de toolmap en vul API keys of poorten in (zie per-tool README).

## Gebruik

### Interactief Menu (Aanbevolen)

Start de suite met:

```bash
python3 jacops.py
```

Of maak het script uitvoerbaar en run direct:

```bash
chmod +x jacops.py
./jacops.py
```

Je krijgt een interactief menu waar je kunt kiezen tussen de beschikbare tools.

### Direct Tool Gebruik

Je kunt ook individuele tools direct gebruiken zonder het hoofdmenu. Zie [CLI_COMMANDS.md](CLI_COMMANDS.md) voor gedetailleerde command line instructies voor elke tool.

## Beschikbare Tools

### [1] File Type Identifier (FTI)
**Directory:** `FTI/`  
Identificeert bestandstypen op basis van magic numbers en detecteert mogelijke spoofing.
- **CLI**: Directe bestandsanalyse via command line met tab completion
- **GUI**: Web-gebaseerde interface op `http://localhost:8000`
- **Features**: Magic number detection, VirusTotal integratie, entropy analyse

### [2] Phishing Email Simulator (PES)
**Directory:** `PES/`  
Simuleert phishing email campagnes voor security awareness training.
- **Web Interface**: Volledige web applicatie met dashboard
- **Features**: Email templates, campagne management, resultaten tracking

### [3] Network Device Scanner (NDT)
**Directory:** `NDT/`  
Scant netwerken voor actieve apparaten en voert OSINT lookups uit.
- **Web Interface**: Dashboard met netwerk scan resultaten op `http://localhost:5001`
- **Features**: Automatische subnet detectie, MAC-adres identificatie, OSINT integratie, port scanning

### [4] Live Threat Intelligence Dashboard (LTID)
**Directory:** `LTID/`  
Real-time threat intelligence aggregatie van meerdere bronnen.
- **Web Dashboard**: Op `http://localhost:8001` (FastAPI, WebSocket)
- **Features**: Real-time threat feeds, IP/domain reputation, malware detection

### [5] Password Policy Analyzer (PPA)
**Directory:** `PPA/`  
Analyseert password policies tegen industry standards.
- **CLI**: Command-line tool met gedetailleerde rapporten
- **Web Interface**: Flask web applicatie
- **Features**: NIST/OWASP compliance checking, security scoring

### [6] Caesar Cipher Frequency Analyzer (CCFA)
**Directory:** `CCFA/`  
Kraakt Caesar ciphers met frequency analysis.
- **CLI**: Interactieve command-line decoder
- **GUI**: Tkinter GUI applicatie
- **Features**: Automatische shift detection, frequency analysis, multi-language support

### [7] DoS Attack Detector (DSAD)
**Directory:** `DSAD/`  
Detecteert Denial of Service aanvallen door netwerkverkeer te monitoren.
- **CLI**: Command-line detector met configuratie en DoS-test
- **GUI**: Webinterface op `http://localhost:8005`
- **Features**: Real-time traffic monitoring, threshold configuration, alert system

### [8] Secure File Sharing System (SFS)
**Directory:** `SFS/`  
Beveiligd bestanden delen met encryptie en tijdelijke links.
- **Web Interface**: Op `http://localhost:8003`
- **Features**: Encryptie, tijdslimiet, token-gebaseerde downloads

### [9] Intrusion Detection Monitor (IDM)
**Directory:** `IDM/`  
Monitor op mislukte logins en brute-force in auth-log.
- **CLI**: Menu met monitoring en configuratie
- **GUI**: Webinterface op `http://localhost:8006`
- **Features**: auth.log-monitoring, drempels, alerts

### [10] Web Vulnerability Scanner (WVS)
**Directory:** `WVS/`  
Scant websites op o.a. SQL-injectie, XSS, directory traversal.
- **CLI**: Scan via menu
- **GUI**: Webinterface op `http://localhost:8004`
- **Features**: Meerdere scantypes, severity-rapportage

## Tool Structuur

Elke tool heeft zijn eigen directory met:
- Tool-specifieke code en modules
- Eigen `requirements.txt` met dependencies
- Eigen `README.md` met gedetailleerde documentatie en gebruiksinstructies
- Configuratiebestanden (indien nodig)

### Directory Overzicht

- **FTI/** – File Type Identifier  
- **PES/** – Phishing Email Simulator  
- **NDT/** – Network Device Scanner  
- **LTID/** – Live Threat Intelligence Dashboard  
- **PPA/** – Password Policy Analyzer  
- **CCFA/** – Caesar Cipher Frequency Analyzer  
- **DSAD/** – DoS Attack Detector  
- **SFS/** – Secure File Sharing System  
- **IDM/** – Intrusion Detection Monitor  
- **WVS/** – Web Vulnerability Scanner  

Zie **[PORTS.md](PORTS.md)** voor het overzicht van poorten per tool.

## CLI vs GUI Keuze

Voor tools die zowel CLI als GUI/web interfaces hebben, krijg je een prompt om te kiezen:
- **[1] CLI versie**: Voor command-line gebruik (sneller, scriptable)
- **[2] GUI versie**: Voor grafische/web interface (gebruiksvriendelijker, visueel)

## Navigatie in de Suite

- **Hoofdmenu**: Kies een tool nummer (1-10) of 0 om te stoppen
- **Terug naar hoofdmenu**: 
  - In CLI tools: Typ 'q' en druk Enter
  - In GUI tools: Druk Ctrl+C
- **Applicatie stoppen**: Druk Ctrl+C in het hoofdmenu

## Requirements

Elke tool heeft zijn eigen requirements. Bekijk de `requirements.txt` in elke tool directory voor specifieke dependencies.

### Gemeenschappelijke Dependencies

- Python 3.7+
- Flask (voor web tools)
- Tkinter (voor GUI tools - meestal al geïnstalleerd met Python)
- Verschillende security libraries per tool

### Tool-specifieke Dependencies

Zie de individuele tool README's voor complete dependency lijsten.

## Documentatie

- **[CLI_COMMANDS.md](CLI_COMMANDS.md)** – Command line referentie voor de suite en alle tools
- **[PORTS.md](PORTS.md)** – Overzicht van poorten per tool (geen conflicten)
- **Tool README's** – Gedetailleerde documentatie per tool in de respectievelijke directories

## Licentie

Dit project valt onder de [MIT License](LICENSE).

## Contributie

Bijdragen zijn welkom. Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor richtlijnen. Bij beveiligingsproblemen: [SECURITY.md](SECURITY.md).

## Versie

**v.1.0** – Suite met 10 tools (8 met web/CLI, 2 optioneel)

### Changelog

- **v.1.0** (Februari 2025)
  - Eerste release
  - 10 tools: FTI, PES, NDT, LTID, PPA, CCFA, DSAD, SFS, IDM, WVS
  - Interactief hoofdmenu met centering en kleuren
  - Tab completion voor file paths
  - Elk tool met eigen poort (zie PORTS.md)
  - Verbeterde UI/UX

## Support

Voor vragen of problemen:
1. Bekijk eerst de tool-specifieke README's
2. Controleer [CLI_COMMANDS.md](CLI_COMMANDS.md) voor command line opties
3. Open een issue in de repository
