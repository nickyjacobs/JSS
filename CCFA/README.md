# Caesar Cipher Decoder met Frequency Analysis

Een geavanceerde Caesar cipher decoder die automatisch encrypted berichten kan kraken zonder kennis van de shift waarde, gebruikmakend van frequency analysis.

## ✨ Features

- 🌐 **Moderne Web GUI**: Professionele donkerblauwe interface die in de browser draait
- 🔓 **Automatische decryptie**: Vindt automatisch de juiste shift waarde zonder handmatige input
- 📊 **Frequency Analysis**: Gebruikt Engelse letter frequenties om de beste match te vinden
- 🎯 **Chi-squared statistiek**: Berekent de beste match met behulp van chi-squared test
- 🔍 **Alle pogingen bekijken**: Optioneel alle 26 mogelijke decrypties tonen met scores
- 📈 **Frequentie analyse**: Analyseer letter frequenties van willekeurige tekst
- 🔒 **Encryptie modus**: Ook mogelijk om berichten te encrypten met een shift waarde
- 💻 **Command Line Interface**: Volledige CLI voor gebruik zonder GUI
- 🧪 **Test Suite**: Automatische tests om functionaliteit te verifiëren

## 🚀 Quick Start

### Web GUI (Aanbevolen)

```bash
python3 caesar_web_gui.py
```

Open dan je browser en ga naar: **http://localhost:8000**

De web GUI biedt:
- Moderne donkerblauwe interface
- Automatische decryptie met één klik
- Handmatige encryptie met shift waarde
- Visuele weergave van resultaten
- Top 5 meest waarschijnlijke decrypties met confidence scores
- Professionele SVG iconen (geen emoji's)

### Command Line Interface

```bash
python3 caesar_decoder.py
```

Interactieve CLI met opties voor:
- Automatische decryptie
- Handmatige encryptie
- Frequentie analyse
- Test voorbeelden

### Programmatisch Gebruik

```python
from caesar_decoder import CaesarDecoder

decoder = CaesarDecoder()

# Encrypt een bericht
encrypted = decoder.encrypt("HELLO WORLD", shift=3)
print(encrypted)  # KHOOR ZRUOG

# Kraak automatisch
result = decoder.crack(encrypted)
print(f"Shift: {result['shift']}")
print(f"Decrypted: {result['decrypted']}")

# Met alle pogingen
result = decoder.crack(encrypted, show_all=True)
for attempt in result['all_attempts'][:5]:
    print(f"Shift {attempt['shift']}: {attempt['text']} (score: {attempt['score']:.2f})")
```

## 📖 Hoe het werkt

### Frequency Analysis

Het programma gebruikt de bekende frequenties van letters in de Engelse taal. De meest voorkomende letters zijn bijvoorbeeld:
- **E**: 12.7%
- **T**: 9.1%
- **A**: 8.2%
- **O**: 7.5%

### Chi-squared Test

Voor elke mogelijke shift (0-25) wordt de chi-squared statistiek berekend. Deze meet hoe goed de letter frequenties van de gedecrypteerde tekst overeenkomen met de verwachte Engelse frequenties. Een lagere chi-squared waarde betekent een betere match.

### Automatische Shift Detectie

Het programma test alle 26 mogelijke shifts en kiest degene met de laagste chi-squared score als de meest waarschijnlijke decryptie.

## 📁 Project Structuur

```
CCFA/
├── caesar_decoder.py      # Core decoder class en CLI
├── caesar_web_gui.py       # Web-based GUI (aanbevolen)
├── caesar_gui.py           # Tkinter GUI (werkt niet op alle systemen)
├── test_decoder.py         # Test suite
├── demo.py                 # Demo script met voorbeelden
├── README.md               # Deze file
├── requirements.txt        # Dependencies (geen externe nodig)
├── LICENSE                 # MIT License
└── .gitignore             # Git ignore regels
```

## 💻 Vereisten

- **Python 3.6+** (getest op Python 3.9+)
- **Geen externe dependencies** - gebruikt alleen Python standaard library modules:
  - `string`
  - `collections`
  - `typing`
  - `http.server` (voor web GUI)
  - `json` (voor web GUI API)

## 📝 Gebruik Voorbeelden

### Voorbeeld 1: Automatische Decryptie

```python
from caesar_decoder import CaesarDecoder

decoder = CaesarDecoder()
message = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
encrypted = decoder.encrypt(message, shift=3)
# Resultaat: WKH TXLFN EURZQ IRA MXPSV RYHU WKH ODCB GRJ

result = decoder.crack(encrypted)
# Automatisch gevonden: shift = 3
# Decrypted: THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG
```

### Voorbeeld 2: Langere Tekst

```python
long_text = """
THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG. 
THIS IS A LONGER TEXT TO TEST FREQUENCY ANALYSIS.
THE MORE TEXT WE HAVE, THE BETTER THE RESULTS WILL BE.
"""

encrypted = decoder.encrypt(long_text, shift=7)
result = decoder.crack(encrypted)
print(f"Gevonden shift: {result['shift']}")
print(f"Confidence: {result['confidence_score']:.2f}")
```

## 🧪 Testing

Voer de test suite uit:

```bash
python3 test_decoder.py
```

Dit test:
- Basis encryptie/decryptie
- Frequency analysis
- Automatische shift detectie
- Langere teksten
- Gemengde hoofdletters/kleine letters

## 💡 Tips & Best Practices

- **Langere teksten**: Werkt het beste met teksten van 50+ karakters
- **Engelse tekst**: Geoptimaliseerd voor Engelse letter frequenties
- **Korte teksten**: Bij zeer korte teksten (< 20 karakters) kan de shift soms verkeerd zijn
- **Case behoud**: Hoofdletters en kleine letters worden correct behouden
- **Leestekens**: Leestekens en spaties worden niet beïnvloed door de encryptie

## 📊 Resultaten Interpretatie

- **Confidence Score**: Lagere waarde = betere match met Engels
- **Alle pogingen**: Gebruik `show_all=True` om alle 26 mogelijke decrypties te zien
- **Top 5**: Als de eerste poging niet klopt, bekijk de top 5 meest waarschijnlijke shifts

## 🎨 GUI Features

### Web GUI (caesar_web_gui.py)
- ✅ Werkt op alle systemen (geen tkinter nodig)
- ✅ Moderne donkerblauwe interface
- ✅ Professionele SVG iconen
- ✅ Responsive design
- ✅ Real-time character counter
- ✅ Shift controls met +/- knoppen

### Tkinter GUI (caesar_gui.py)
- ⚠️ Werkt niet op alle macOS versies
- Gebruik de web GUI als alternatief

## 🤝 Contributing

Contributions zijn welkom! Voel je vrij om:
- Issues te melden
- Pull requests in te dienen
- Verbeteringen voor te stellen

## 📄 License

Dit project is gelicenseerd onder de MIT License - zie het [LICENSE](LICENSE) bestand voor details.

## 👤 Auteur

Gemaakt voor automatische decryptie van Caesar cipher berichten met frequency analysis.

## 🙏 Acknowledgments

- Gebaseerd op klassieke frequency analysis technieken
- Engelse letter frequenties gebaseerd op standaard cryptografie bronnen
