# JacOps Security Suite v1.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Een uitgebreide cybersecurity multitool suite met 10 professionele security tools. Alle tools zijn toegankelijk via een centraal interactief menu (CLI en/of web-GUI).

<img width="1259" height="754" alt="image" src="https://github.com/user-attachments/assets/cadb9e34-89e7-4c83-b1fd-7fd088baa644" />

## Overzicht

- **Eén menu** – Start `python3 jacops.py` en kies een tool (1–10).
- **CLI en GUI** – Veel tools bieden zowel command-line als webinterface.
- **Geen poortconflicten** – Elke tool heeft een vaste poort; zie [PORTS.md](PORTS.md).

## Installatie

1. **Clone de repository**
   ```bash
   git clone https://github.com/nickyjacobs/JSS.git
   cd JSS
   ```
   De repo is publiek; iedereen kan clonen zonder in te loggen.

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

![SCR-20260218-pdac](https://github.com/user-attachments/assets/745e193c-5148-4fd2-8975-6c7d93c5051f)

### [1] File Type Identifier (FTI)
**Directory:** `FTI/`  
Identificeert bestandstypen op basis van magic numbers en detecteert mogelijke spoofing.
- **CLI**: Directe bestandsanalyse via command line met tab completion
- **GUI**: Web-gebaseerde interface op `http://localhost:8000`
- **Features**: Magic number detection, VirusTotal integratie, entropy analyse

### [2] Phishing Email Simulator (PES) 
#### Unavailable at the moment
**Directory:** `PES/`  
Simuleert phishing email campagnes voor security awareness training.
- **Web Interface**: Volledige web applicatie met dashboard
- **Features**: Email templates, campagne management, resultaten tracking

![SCR-20260218-pcny](https://github.com/user-attachments/assets/94355505-bf7d-4ac6-a34d-4ed84823cae9)

### [3] Network Device Scanner (NDT)
**Directory:** `NDT/`  
Scant netwerken voor actieve apparaten en voert OSINT lookups uit.
- **Web Interface**: Dashboard met netwerk scan resultaten op `http://localhost:5001`
- **Features**: Automatische subnet detectie, MAC-adres identificatie, OSINT integratie, port scanning

![SCR-20260218-pchm](https://github.com/user-attachments/assets/94515068-68a4-4c3d-adec-0e41da2fb87b)

### [4] Live Threat Intelligence Dashboard (LTID)
**Directory:** `LTID/`  
Real-time threat intelligence aggregatie van meerdere bronnen.
- **Web Dashboard**: Op `http://localhost:8001` (FastAPI, WebSocket)
- **Features**: Real-time threat feeds, IP/domain reputation, malware detection

![SCR-20260218-pdkl](https://github.com/user-attachments/assets/0af20d73-5b61-4b9f-89c3-4b1d9f432576)

### [5] Password Policy Analyzer (PPA)
**Directory:** `PPA/`  
Analyseert password policies tegen industry standards.
- **CLI**: Command-line tool met gedetailleerde rapporten
- **Web Interface**: Flask web applicatie
- **Features**: NIST/OWASP compliance checking, security scoring

![SCR-20260218-pdzb](https://github.com/user-attachments/assets/807c5555-c5d1-41fd-a576-24168a8aa78a)

### [6] Caesar Cipher Frequency Analyzer (CCFA)
**Directory:** `CCFA/`  
Kraakt Caesar ciphers met frequency analysis.
- **CLI**: Interactieve command-line decoder
- **GUI**: Tkinter GUI applicatie
- **Features**: Automatische shift detection, frequency analysis, multi-language support

![SCR-20260218-pfoe](https://github.com/user-attachments/assets/7f184fcb-b764-461f-a0d5-9867fc474fc5)

### [7] DoS Attack Detector (DSAD)
**Directory:** `DSAD/`  
Detecteert Denial of Service aanvallen door netwerkverkeer te monitoren.
- **CLI**: Command-line detector met configuratie en DoS-test
- **GUI**: Webinterface op `http://localhost:8005`
- **Features**: Real-time traffic monitoring, threshold configuration, alert system

![SCR-20260218-pgdo](https://github.com/user-attachments/assets/23b4ec1c-757e-46cf-a2d5-8bad8acd688f)

### [8] Secure File Sharing System (SFS)
**Directory:** `SFS/`  
Beveiligd bestanden delen met encryptie en tijdelijke links.
- **Web Interface**: Op `http://localhost:8003`
- **Features**: Encryptie, tijdslimiet, token-gebaseerde downloads

![SCR-20260218-pgmp](https://github.com/user-attachments/assets/d377e3f2-b657-4c08-8129-6ae23ca7f990)

### [9] Intrusion Detection Monitor (IDM)
**Directory:** `IDM/`  
Monitor op mislukte logins en brute-force in auth-log.
- **CLI**: Menu met monitoring en configuratie
- **GUI**: Webinterface op `http://localhost:8006`
- **Features**: auth.log-monitoring, drempels, alerts

![SCR-20260218-pgrv](https://github.com/user-attachments/assets/00088acf-b5bd-4604-a0d2-e03691b7ad12)

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
