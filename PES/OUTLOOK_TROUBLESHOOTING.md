# Outlook Authenticatie Probleem Oplossen

Je krijgt een authenticatie fout. Hier zijn de stappen om dit op te lossen:

## Stap 1: Controleer je Wachtwoord

1. **Test eerst of je kunt inloggen op Outlook.com:**
   - Ga naar: https://outlook.com
   - Log in met: `nicky.jacobs98@outlook.com` en je wachtwoord
   - Als dit niet werkt, is je wachtwoord verkeerd

## Stap 2: Check of je 2FA hebt

Als je 2-Factor Authenticatie hebt ingeschakeld, moet je een App Password maken:

1. **Ga naar Microsoft Account Security:**
   - https://account.microsoft.com/security

2. **Log in met je Outlook account**

3. **Zoek naar "App passwords" of "App-wachtwoorden":**
   - Als je dit niet ziet, heb je waarschijnlijk geen 2FA → gebruik je normale wachtwoord
   - Als je dit wel ziet, maak een nieuw App Password aan

4. **Maak een App Password:**
   - Klik op "App passwords" of "App-wachtwoorden"
   - Selecteer "Mail" en geef het een naam (bijv. "Phishing Simulator")
   - Klik op "Generate" of "Genereren"
   - Kopieer het gegenereerde wachtwoord (16 karakters)

5. **Gebruik het App Password in je .env bestand:**
   ```env
   SMTP_PASSWORD=het-app-password-dat-je-net-hebt-gekregen
   ```

## Stap 3: Probeer Alternatieve Instellingen

Als je normale wachtwoord niet werkt, probeer deze alternatieve instellingen:

### Optie A: Poort 465 met SSL
Pas je `.env` bestand aan:
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=465
SMTP_USE_TLS=false
SMTP_USE_SSL=true
```

### Optie B: smtp.office365.com (soms werkt dit beter)
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

## Stap 4: Herstart de Applicatie

Na het aanpassen van je `.env` bestand:
1. Stop de applicatie (Ctrl+C in de terminal)
2. Start opnieuw: `python3 app.py`
3. Test opnieuw via de web interface

## Veelvoorkomende Problemen

### "Account is geblokkeerd"
- Microsoft kan je account tijdelijk blokkeren bij verdachte activiteit
- Wacht 15-30 minuten en probeer opnieuw
- Log eerst in op outlook.com om te bevestigen dat je account actief is

### "Wachtwoord werkt niet"
- Controleer of je geen extra spaties hebt gekopieerd
- Test eerst inloggen op outlook.com
- Als je 2FA hebt, gebruik een App Password

### "Server verbinding verbroken"
- Controleer je internet verbinding
- Probeer een andere netwerkverbinding
- Sommige netwerken blokkeren SMTP poorten

## Hulp Nodig?

Als niets werkt:
1. Controleer of je account niet geblokkeerd is op outlook.com
2. Probeer eerst in te loggen op outlook.com met je gegevens
3. Als dat werkt maar SMTP niet, heb je waarschijnlijk 2FA en moet je een App Password gebruiken
