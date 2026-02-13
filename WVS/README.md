# Web Vulnerability Scanner (WVS)

Een web vulnerability scanner die websites scant op veelvoorkomende beveiligingskwetsbaarheden zoals SQL injection, XSS, directory traversal, command injection en onveilige file uploads.

## Features

- 🔍 **SQL Injection Detection**: Detecteert potentiële SQL injection kwetsbaarheden
- ⚠️ **XSS Detection**: Vindt Cross-Site Scripting kwetsbaarheden
- 📁 **Directory Traversal**: Test op directory traversal kwetsbaarheden
- 💻 **Command Injection**: Detecteert command injection mogelijkheden
- 📤 **File Upload Security**: Controleert file upload formulieren op beveiligingsproblemen
- 💻 **CLI & Web GUI**: Volledige ondersteuning voor zowel command-line als web interface
- 📊 **Gedetailleerde Rapportage**: Uitgebreide rapporten met severity levels

## Requirements

- Python 3.9 of hoger
- pip (Python package manager)

## Installatie

### Optie 1: Via jacops.py (Aanbevolen)

Het Web Vulnerability Scanner is geïntegreerd in de JacOps Security Suite. Start het via:

```bash
python3 jacops.py
```

Selecteer optie `[10] Web Vulnerability Scanner` en kies tussen CLI of GUI.

### Optie 2: Handmatig

```bash
cd WVS

# Maak virtual environment aan (eerste keer)
python3 -m venv .venv
source .venv/bin/activate  # Op Windows: .venv\Scripts\activate

# Installeer dependencies
pip install -r requirements.txt
```

## Gebruik

### Web Interface

Start de web interface:

```bash
python3 app.py
```

Open vervolgens je browser naar `http://localhost:8004`

**Features:**
- Eenvoudige URL invoer
- Selecteerbare scan types
- Real-time scan resultaten
- Severity-gecodeerde kwetsbaarheden
- Gedetailleerde rapportage

### Command Line Interface (CLI)

Start de CLI:

```bash
python3 cli.py
```

**Menu opties:**
1. **Scan website**: Scan een website op kwetsbaarheden
2. **Afsluiten**: Terug naar hoofdmenu

**Scan Types:**
- Alle scans (standaard)
- SQL Injection
- XSS (Cross-Site Scripting)
- Directory Traversal
- Command Injection
- File Upload

## Configuratie

Bewerk `config.py` of maak een `.env` bestand aan:

```env
WVS_HOST=127.0.0.1
WVS_PORT=8004
WVS_TIMEOUT=10  # Seconden
WVS_MAX_CONCURRENT=10
WVS_USER_AGENT=Mozilla/5.0...
WVS_ENABLE_SQL=true
WVS_ENABLE_XSS=true
WVS_ENABLE_DIR_TRAV=true
WVS_ENABLE_CMD_INJ=true
WVS_ENABLE_FILE_UPLOAD=true
```

## Gedetecteerde Kwetsbaarheden

### SQL Injection
- Detecteert SQL foutmeldingen in responses
- Test verschillende SQL payloads
- Ondersteunt MySQL, PostgreSQL, SQLite, Oracle

### XSS (Cross-Site Scripting)
- Test op reflected XSS
- Verschillende XSS payloads
- Detecteert payload reflectie in responses

### Directory Traversal
- Test op path traversal kwetsbaarheden
- Detecteert toegang tot systeembestanden
- Verschillende encoding methoden

### Command Injection
- Detecteert command execution
- Test verschillende injection methoden
- Detecteert command output in responses

### File Upload
- Controleert file upload formulieren
- Checkt op ontbrekende security headers
- Identificeert potentiële upload kwetsbaarheden

## Severity Levels

- **Critical**: Directe code execution mogelijk
- **High**: Significante beveiligingsrisico's
- **Medium**: Matige beveiligingsrisico's
- **Low**: Kleine beveiligingsproblemen

## Beveiliging

⚠️ **BELANGRIJK**: 
- Gebruik deze tool alleen op websites waar je toestemming hebt om te scannen
- Ongeautoriseerd scannen van websites is illegaal
- Gebruik alleen voor security testing van je eigen applicaties
- Wees voorzichtig met automatische scans op productie systemen

## Bestandsstructuur

```
WVS/
├── app.py              # Flask web applicatie
├── cli.py              # Command-line interface
├── scanner.py          # Core scanning functionaliteit
├── config.py           # Configuratie instellingen
├── requirements.txt    # Python dependencies
├── README.md          # Deze documentatie
├── results/           # Scan resultaten (optioneel)
└── templates/         # HTML templates
    └── index.html     # Web interface
```

## API Endpoints

### POST `/api/scan`
Run een vulnerability scan.

**JSON body:**
```json
{
  "url": "https://example.com",
  "scan_types": ["all"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "vulnerabilities": [
      {
        "type": "sql_injection",
        "severity": "high",
        "title": "Potential SQL Injection",
        "description": "SQL error detected",
        "url": "https://example.com/page",
        "payload": "' OR '1'='1"
      }
    ],
    "count": 1
  }
}
```

## Licentie

Onderdeel van de JacOps Security Suite.
