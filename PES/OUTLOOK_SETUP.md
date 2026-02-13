# Outlook Email Configuratie - Stap voor Stap

## ✅ Outlook Instellingen

Je `.env` bestand is nu ingesteld voor Outlook! Hier is wat je moet doen:

## Stap 1: Vul je Outlook Gegevens In

Open het `.env` bestand en pas deze regels aan:

```env
SMTP_USERNAME=jouw-email@outlook.com
SMTP_PASSWORD=jouw-wachtwoord-hier
```

**Voorbeelden:**
- `SMTP_USERNAME=jantje@outlook.com`
- `SMTP_USERNAME=jantje@hotmail.com`
- `SMTP_USERNAME=jantje@live.com`

Alle drie werken hetzelfde! Outlook, Hotmail en Live.com gebruiken dezelfde SMTP server.

## Stap 2: Wachtwoord

### Optie A: Normaal Wachtwoord (meestal werkt dit)
Gebruik gewoon je normale Outlook wachtwoord.

### Optie B: Als je 2-Factor Authenticatie hebt
Als je 2FA hebt ingeschakeld, moet je mogelijk een App Password gebruiken:
1. Ga naar: https://account.microsoft.com/security
2. Log in met je Outlook account
3. Ga naar "App passwords" of "App-wachtwoorden"
4. Maak een nieuw app password aan
5. Gebruik dat wachtwoord in plaats van je normale wachtwoord

## Stap 3: Test je Configuratie

1. **Start de applicatie:**
   ```bash
   cd /Users/nicky/Desktop/MCST/PES
   python3 app.py
   ```

2. **Open je browser:**
   Ga naar: `http://localhost:5000`

3. **Test je email:**
   - Klik op "Instellingen" in het menu
   - Controleer of je gegevens correct zijn ingevuld
   - Klik op "Test Email Verzenden"
   - Voer je eigen Outlook email adres in
   - Check je inbox (en spam folder!)

## ✅ Outlook SMTP Instellingen (al ingesteld)

```
SMTP Server: smtp-mail.outlook.com
Poort: 587
Encryptie: TLS
```

Deze instellingen staan al correct in je `.env` bestand!

## Problemen Oplossen

### "Authenticatie fout"
- Controleer of je email adres correct is (volledig adres inclusief @outlook.com)
- Controleer je wachtwoord
- Als je 2FA hebt: gebruik een App Password

### "Server verbinding verbroken"
- Controleer je internet verbinding
- Sommige netwerken blokkeren poort 587
- Probeer een andere netwerkverbinding (bijv. mobiele hotspot)

### Email komt niet aan
- Check je spam/junk folder
- Controleer of het email adres correct is
- Test eerst met je eigen email adres

## Klaar!

Als de test email aankomt, werkt alles perfect! 🎉

Je kunt nu beginnen met het aanmaken van phishing campaigns voor security awareness training.
