# Password Policy Analyzer (PPA)

Een geavanceerde tool die organisatie wachtwoordbeleid evalueert tegen industry standards zoals NIST 800-63B en OWASP richtlijnen. De tool analyseert niet alleen de sterkte van wachtwoordvereisten, maar biedt ook concrete verbeteringsvoorstellen met referenties naar echte datalek statistieken.

## Features

- ✅ Evaluatie tegen NIST 800-63B richtlijnen
- ✅ OWASP password policy checks
- ✅ Real-world breach statistics referenties
- ✅ Concrete verbeteringsvoorstellen
- ✅ Moderne web interface met dark theme
- ✅ **Command-line interface (CLI)** voor terminal gebruik
- ✅ Meertalige ondersteuning (Nederlands/English)
- ✅ Export functionaliteit voor rapporten (HTML & JSON)
- ✅ Uitgebreide uitleg waarom elke verandering belangrijk is

## Requirements

- Python 3.9 of hoger
- pip (Python package manager)

## Installatie

### Optie 1: Gebruik het startup script (aanbevolen)

```bash
chmod +x run.sh
./run.sh
```

### Optie 2: Handmatig

```bash
# Maak virtual environment aan (eerste keer)
python3 -m venv venv
source venv/bin/activate  # Op Windows: venv\Scripts\activate

# Installeer dependencies
pip install -r requirements.txt

# Start de applicatie
python app.py
```

Open vervolgens je browser naar `http://localhost:5500`

## Gebruik

### Web Interface

1. Open de web interface in je browser
2. Vul je password policy in via het formulier
3. Klik op "Analyseer Policy"
4. Bekijk de resultaten met severity levels (Critical, High, Medium, Low)
5. Exporteer een rapport indien gewenst

### Command Line Interface (CLI)

De tool kan ook gebruikt worden vanuit de terminal:

```bash
# Analyseer een policy vanuit een JSON bestand
python cli.py --file example_policy.json

# Analyseer met command-line argumenten
python cli.py --min-length 8 --prevent-common-passwords --prevent-user-info

# Exporteer resultaten naar JSON
python cli.py --file example_policy.json --export report.json

# Gebruik Engelse taal
python cli.py --file example_policy.json --lang en

# Alleen JSON output (voor scripting)
python cli.py --file example_policy.json --json

# Zie alle opties
python cli.py --help
```

#### CLI Voorbeelden

```bash
# Volledige policy analyse
python cli.py \
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

# Eenvoudige analyse
python cli.py --file example_policy.json --lang en --export report.json

# Alleen JSON output (voor scripting/automation)
python cli.py --file example_policy.json --json > results.json
```

#### CLI Output

De CLI tool geeft kleurrijke, geformatteerde output met:
- Security score en grade
- Findings gegroepeerd per severity level
- Aanbevelingen en standaard referenties
- Optionele JSON export voor verdere verwerking

#### Exit Codes

- `0`: Succesvol (geen critical findings)
- `1`: Succesvol maar met critical findings (of error)

## Policy Checks

De tool evalueert de volgende aspecten van je password policy:

### NIST 800-63B Checks
- **Minimale wachtwoordlengte**: Vereist minimaal 8 karakters (aanbevolen: 12+)
- **Maximale wachtwoordlengte**: Moet minimaal 64 karakters toestaan voor passphrases
- **Complexity vereisten**: NIST raadt aan om lengte boven complexity te prioriteren
- **Wachtwoordverlopen**: Geforceerde verlopen wordt afgeraden
- **Wachtwoordgeschiedenis**: Moet voorkomen dat gebruikers oude wachtwoorden hergebruiken
- **Common password check**: Moet controleren op veelvoorkomende/gecompromitteerde wachtwoorden

### OWASP Checks
- **Account lockout**: Moet brute force aanvallen voorkomen
- **Gebruikersinformatie**: Moet voorkomen dat gebruikersinformatie in wachtwoorden wordt gebruikt
- **Herhalende karakters**: Moet voorkomen dat gebruikers veel herhalende karakters gebruiken
- **Sequentiële karakters**: Moet voorkomen dat gebruikers sequentiële patronen gebruiken

## Severity Levels

- **Critical**: Directe beveiligingsrisico's die onmiddellijk moeten worden aangepakt
- **High**: Belangrijke beveiligingsproblemen die prioriteit moeten krijgen
- **Medium**: Beveiligingsverbeteringen die aanbevolen zijn
- **Low**: Best practices en verbeteringen met lagere prioriteit

## Industry Standards

De tool evalueert tegen:
- **NIST 800-63B**: Digital Identity Guidelines - Authentication and Lifecycle Management
- **OWASP**: Password Storage Cheat Sheet en Authentication Cheat Sheet

## Project Structuur

```
PPA/
├── app.py                 # Flask web application
├── cli.py                 # Command-line interface
├── policy_analyzer.py     # Core analysis engine
├── requirements.txt        # Python dependencies
├── run.sh                 # Startup script
├── README.md              # Deze file
├── CONTRIBUTING.md        # Contributie guidelines
├── .gitignore             # Git ignore rules
├── example_policy.json    # Voorbeeld policy configuratie
└── templates/
    └── index.html         # Frontend HTML/CSS/JavaScript
```

## Development

### Debug Mode

Om debug mode in te schakelen:

```bash
export FLASK_DEBUG=true
python app.py
```

Of gebruik de environment variable:

```bash
FLASK_DEBUG=true python app.py
```

**Waarschuwing**: Debug mode moet NIET worden gebruikt in productie!

### Dependencies

- `flask==3.0.0`: Web framework
- `flask-cors==4.0.0`: Cross-Origin Resource Sharing support
- `python-dotenv==1.0.0`: Environment variable management

## Contributing

1. Fork het project
2. Maak een feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit je wijzigingen (`git commit -m 'Add some AmazingFeature'`)
4. Push naar de branch (`git push origin feature/AmazingFeature`)
5. Open een Pull Request

## License

Dit project is open source en beschikbaar onder de MIT License.

## Auteurs

- Ontwikkeld voor MCST

## Referenties

- [NIST SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
