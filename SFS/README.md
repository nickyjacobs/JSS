# Secure File Sharing System (SFS)

Een veilig bestandsdeling systeem met encryptie, tijdsgebonden toegang en wachtwoordbescherming. Bestanden worden automatisch versleuteld opgeslagen en kunnen veilig gedeeld worden via unieke tokens.

## Features

- 🔒 **End-to-end encryptie**: Bestanden worden versleuteld opgeslagen met Fernet (AES-128)
- 🔑 **Wachtwoordbescherming**: Optionele wachtwoordbescherming per bestand
- ⏰ **Tijdsgebonden toegang**: Automatische verloopdatum voor bestanden
- 📊 **Download tracking**: Houdt bij hoeveel keer een bestand is gedownload
- 🗑️ **Automatische cleanup**: Verlopen bestanden worden automatisch verwijderd
- 💻 **CLI & Web GUI**: Volledige ondersteuning voor zowel command-line als web interface
- 🔐 **Veilige token generatie**: Cryptografisch veilige tokens voor bestandsdeling

## Requirements

- Python 3.9 of hoger
- pip (Python package manager)

## Installatie

### Optie 1: Via jacops.py (Aanbevolen)

Het Secure File Sharing System is geïntegreerd in de JacOps Security Suite. Start het via:

```bash
python3 jacops.py
```

Selecteer optie `[8] Secure File Sharing System` en kies tussen CLI of GUI.

### Optie 2: Handmatig

```bash
cd SFS

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

Open vervolgens je browser naar `http://localhost:8003`

**Features:**
- Drag & drop bestand upload
- Bestandslijst met alle actieve bestanden
- Download via token
- Wachtwoordbescherming
- Automatische verloopdatum

### Command Line Interface (CLI)

Start de CLI:

```bash
python3 cli.py
```

**Menu opties:**
1. **Upload bestand**: Upload een bestand met optionele wachtwoordbescherming
2. **Download bestand**: Download een bestand met token en wachtwoord
3. **Lijst actieve bestanden**: Toon alle actieve bestanden
4. **Verwijder bestand**: Verwijder een bestand met token
5. **Ruim verlopen bestanden op**: Verwijder alle verlopen bestanden

## Configuratie

Bewerk `config.py` of maak een `.env` bestand aan voor aangepaste instellingen:

```env
SFS_HOST=127.0.0.1
SFS_PORT=8003
SFS_MAX_FILE_SIZE=100  # In MB
SFS_TOKEN_LENGTH=32
SFS_DEFAULT_EXPIRY=24  # In uren
```

## Beveiliging

- **Encryptie**: Alle bestanden worden versleuteld met Fernet (AES-128 in CBC mode)
- **Token generatie**: Cryptografisch veilige tokens met `secrets.token_urlsafe()`
- **Wachtwoord hashing**: SHA-256 hashing voor wachtwoordbescherming
- **Automatische cleanup**: Verlopen bestanden worden automatisch verwijderd
- **File size limits**: Configureerbare maximale bestandsgrootte

## Bestandsstructuur

```
SFS/
├── app.py              # Flask web applicatie
├── cli.py              # Command-line interface
├── file_manager.py     # Core file management functionaliteit
├── config.py           # Configuratie instellingen
├── requirements.txt    # Python dependencies
├── README.md          # Deze documentatie
├── storage/           # Bestandsopslag (automatisch aangemaakt)
│   ├── uploads/       # Versleutelde bestanden
│   └── metadata/     # Bestandsmetadata (JSON)
└── templates/        # HTML templates
    └── index.html    # Web interface
```

## API Endpoints

### POST `/api/upload`
Upload een bestand.

**Form data:**
- `file`: Het bestand om te uploaden
- `password`: Optioneel wachtwoord
- `expiry_hours`: Verlooptijd in uren (standaard: 24)

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "unique-token",
    "filename": "example.pdf",
    "expiry_time": "2024-01-02T12:00:00",
    "download_url": "/download/unique-token"
  }
}
```

### GET `/api/list`
Lijst alle actieve bestanden.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "token": "token",
      "filename": "file.pdf",
      "file_size": 1024,
      "upload_time": "2024-01-01T12:00:00",
      "expiry_time": "2024-01-02T12:00:00",
      "download_count": 0,
      "password_protected": false
    }
  ]
}
```

### GET `/api/info/<token>`
Haal bestandsinformatie op.

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "token",
    "filename": "file.pdf",
    "file_size": 1024,
    "expiry_time": "2024-01-02T12:00:00",
    "password_protected": true
  }
}
```

### POST `/api/download/<token>`
Download een bestand.

**JSON body:**
```json
{
  "password": "optional-password"
}
```

**Response:** Bestand download (binary)

### DELETE `/api/delete/<token>`
Verwijder een bestand.

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

### POST `/api/cleanup`
Ruim verlopen bestanden op.

**Response:**
```json
{
  "success": true,
  "deleted_count": 5
}
```

## Veiligheidsoverwegingen

- **Encryptie keys**: De encryptie key wordt automatisch gegenereerd en opgeslagen in `storage/.encryption_key`
- **Token veiligheid**: Tokens zijn cryptografisch veilig en moeilijk te raden
- **Wachtwoordbescherming**: Wachtwoorden worden gehasht met SHA-256 (niet salted - voor productie gebruik bcrypt overwegen)
- **Bestandsopslag**: Bestanden worden versleuteld opgeslagen, maar metadata is in plaintext JSON
- **Network security**: Standaard draait de server alleen op localhost (127.0.0.1)

## Licentie

Onderdeel van de JacOps Security Suite.
