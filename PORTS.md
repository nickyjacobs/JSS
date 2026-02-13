# Poortoverzicht – JacOps Security Suite

Elke tool met een webinterface gebruikt een vaste poort. Zo kunnen meerdere tools naast elkaar draaien zonder conflicten.

| Tool | Standaardpoort | Omgevingsvariabele | Opmerking |
|------|----------------|--------------------|-----------|
| **FTI** (File Type Identifier) | 8000* | — | *Eerste vrije poort in bereik 8000–8010 |
| **PES** (Phishing Email Simulator) | 5000 | `FLASK_PORT` | |
| **NDT** (Network Device Scanner) | 5001 | — | Vast in code |
| **LTID** (Live Threat Intelligence Dashboard) | 8001 | `DASHBOARD_PORT` | |
| **PPA** (Password Policy Analyzer) | 5500 | — | Vast in jacops.py |
| **CCFA** (Caesar Cipher – web) | 8002 | — | Vast in jacops.py |
| **SFS** (Secure File Sharing) | 8003 | `SFS_PORT` | |
| **WVS** (Web Vulnerability Scanner) | 8004 | `WVS_PORT` | |
| **DSAD** (DoS Attack Detector) | 8005 | `DSAD_PORT` | |
| **IDM** (Intrusion Detection Monitor) | 8006 | `IDM_PORT` | |

Geen twee tools delen dezelfde standaardpoort. Poorten wijzigen kan via een `.env` in de betreffende toolmap (waar ondersteund).
