# Outlook Setup - Simpel!

## ✅ Goed Nieuws!

Voor Outlook hoef je **geen App Password** te maken! Je kunt gewoon je **normale Outlook wachtwoord** gebruiken.

## Wat je moet doen:

### Stap 1: Open het `.env` bestand

Open: `/Users/nicky/Desktop/MCST/PES/.env`

### Stap 2: Vul alleen deze 2 regels in:

```env
SMTP_USERNAME=jouw-email@outlook.com
SMTP_PASSWORD=jouw-normale-wachtwoord
```

**Voorbeeld:**
- Als je email `jan@outlook.com` is en je wachtwoord `MijnWachtwoord123!` is:
  ```env
  SMTP_USERNAME=jan@outlook.com
  SMTP_PASSWORD=MijnWachtwoord123!
  ```

### Stap 3: Sla het bestand op

Dat is alles! De rest staat al goed ingesteld.

## Testen

1. Start de app:
   ```bash
   cd /Users/nicky/Desktop/MCST/PES
   python3 app.py
   ```

2. Ga naar: `http://localhost:5000`

3. Klik op "Instellingen" → "Test Email Verzenden"

4. Voer je eigen email in en test!

## Als het niet werkt

Als je een "authenticatie fout" krijgt, kan het zijn dat:

1. **Je wachtwoord verkeerd is** - controleer het nog een keer
2. **Je hebt 2FA ingeschakeld** - dan moet je inderdaad een App Password maken
3. **Je account is geblokkeerd** - probeer eerst in te loggen op outlook.com

Maar in 99% van de gevallen werkt je normale wachtwoord gewoon! 👍

## App Password alleen nodig als...

- Je hebt 2-factor authenticatie (2FA) ingeschakeld
- Je normale wachtwoord niet werkt
- Je een specifieke beveiligingswaarschuwing krijgt

Voor de meeste mensen werkt het normale wachtwoord perfect!
