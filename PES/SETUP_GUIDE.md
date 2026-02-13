# Stap-voor-stap Setup Gids

## Stap 1: Dependencies Installeren ✅
```bash
pip3 install -r requirements.txt
```
**Status:** Voltooid!

## Stap 2: .env Bestand Configureren

Het `.env` bestand is aangemaakt. Nu moet je het invullen met jouw email gegevens.

### Optie A: Gmail Gebruiken (Aanbevolen voor beginners)

1. **Open het `.env` bestand** in een tekst editor (bijv. TextEdit, VS Code, of nano)

2. **Voor Gmail heb je een App Password nodig:**
   - Ga naar: https://myaccount.google.com/apppasswords
   - Log in met je Gmail account
   - Selecteer "Mail" en "Other (Custom name)"
   - Geef het een naam zoals "Phishing Simulator"
   - Klik op "Generate"
   - Kopieer het gegenereerde wachtwoord (16 karakters)

3. **Vul het `.env` bestand in:**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=jouw-echte-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx    # Het App Password dat je net hebt gekregen
   SMTP_USE_TLS=true
   SMTP_USE_SSL=false
   BASE_URL=http://localhost:5000
   ```

   **BELANGRIJK:** 
   - Gebruik je volledige Gmail adres voor SMTP_USERNAME
   - Gebruik het App Password (niet je normale Gmail wachtwoord!)
   - Verwijder de spaties uit het App Password als je het kopieert

### Optie B: Outlook/Hotmail

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@outlook.com
SMTP_PASSWORD=jouw-wachtwoord
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### Optie C: Yahoo

```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@yahoo.com
SMTP_PASSWORD=jouw-app-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### Optie D: Testen zonder Email (Demo Mode)

Als je eerst wilt testen zonder email te configureren, laat je de SMTP_USERNAME en SMTP_PASSWORD leeg:
```env
SMTP_USERNAME=
SMTP_PASSWORD=
```

De applicatie werkt dan in "demo mode" - emails worden niet verzonden, maar je ziet wel wat er zou worden verzonden.

## Stap 3: Applicatie Starten

Open een terminal in de PES map en run:
```bash
python3 app.py
```

Je zou moeten zien:
```
 * Running on http://0.0.0.0:5000
```

## Stap 4: Web Interface Openen

Open je browser en ga naar:
```
http://localhost:5000
```

## Stap 5: Email Configuratie Testen

1. Klik op **"Instellingen"** in het menu
2. Controleer of je email gegevens correct zijn ingevuld
3. Klik op **"Test Email Verzenden"**
4. Voer je eigen email adres in
5. Check je inbox voor de test email

Als de test email aankomt, werkt alles! 🎉

## Problemen Oplossen

### "Authenticatie fout" bij Gmail
- Zorg dat je een **App Password** gebruikt, niet je normale wachtwoord
- Controleer dat 2-factor authenticatie is ingeschakeld
- Verwijder spaties uit het App Password

### "Server verbinding verbroken"
- Controleer je internet verbinding
- Controleer of poort 587 niet geblokkeerd is door firewall
- Probeer poort 465 met SSL: `SMTP_PORT=465` en `SMTP_USE_SSL=true`

### Emails komen niet aan
- Check je spam folder
- Controleer of het email adres correct is
- Test eerst met je eigen email adres

## Volgende Stappen

1. Maak je eerste campaign aan
2. Voeg test email adressen toe
3. Verstuur een test email
4. Bekijk de tracking resultaten

Veel succes! 🚀
