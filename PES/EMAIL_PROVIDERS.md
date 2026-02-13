# Email Provider Configuratie Gids

De Phishing Email Simulator werkt met **alle SMTP providers**! Hier zijn de instellingen voor de meest populaire providers:

## 📧 Ondersteunde Providers

### 1. Gmail
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@gmail.com
SMTP_PASSWORD=jouw-app-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```
**Opmerking:** Je moet een [App Password](https://myaccount.google.com/apppasswords) gebruiken, niet je normale wachtwoord.

---

### 2. Outlook / Hotmail / Live.com
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@outlook.com
SMTP_PASSWORD=jouw-wachtwoord
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```
**Opmerking:** Gebruik je normale Outlook wachtwoord. Als je 2FA hebt, moet je mogelijk een App Password gebruiken.

---

### 3. Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@yahoo.com
SMTP_PASSWORD=jouw-app-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```
**Opmerking:** Yahoo vereist meestal een App Password. Ga naar: https://login.yahoo.com/account/security

---

### 4. ProtonMail
```env
SMTP_SERVER=127.0.0.1
SMTP_PORT=1025
SMTP_USERNAME=jouw-email@protonmail.com
SMTP_PASSWORD=jouw-wachtwoord
SMTP_USE_TLS=false
SMTP_USE_SSL=false
```
**Opmerking:** ProtonMail vereist de ProtonMail Bridge applicatie. Download: https://proton.me/mail/bridge

---

### 5. iCloud Mail
```env
SMTP_SERVER=smtp.mail.me.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@icloud.com
SMTP_PASSWORD=jouw-app-specifiek-wachtwoord
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```
**Opmerking:** Je moet een app-specifiek wachtwoord genereren via: https://appleid.apple.com/

---

### 6. Zoho Mail
```env
SMTP_SERVER=smtp.zoho.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@zoho.com
SMTP_PASSWORD=jouw-wachtwoord
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

---

### 7. Mail.com
```env
SMTP_SERVER=smtp.mail.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@mail.com
SMTP_PASSWORD=jouw-wachtwoord
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

---

### 8. Custom Bedrijfs Email (Microsoft 365 / Exchange)

Als je een bedrijfs email hebt via Microsoft 365:
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@bedrijf.com
SMTP_PASSWORD=jouw-wachtwoord
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

---

### 9. Custom Bedrijfs Email (Algemene SMTP)

Voor andere bedrijfs email servers, vraag je IT afdeling om:
- SMTP server adres
- SMTP poort (meestal 587 of 465)
- Of TLS of SSL wordt gebruikt

Voorbeeld:
```env
SMTP_SERVER=mail.jouwbedrijf.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@jouwbedrijf.com
SMTP_PASSWORD=jouw-wachtwoord
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

---

## 🔒 SSL vs TLS

**Poort 587 met TLS** (meest gebruikelijk):
```env
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

**Poort 465 met SSL** (alternatief):
```env
SMTP_PORT=465
SMTP_USE_TLS=false
SMTP_USE_SSL=true
```

**Poort 25 zonder encryptie** (niet aanbevolen, vaak geblokkeerd):
```env
SMTP_PORT=25
SMTP_USE_TLS=false
SMTP_USE_SSL=false
```

---

## 🧪 Testen van je Configuratie

1. Vul je `.env` bestand in met de juiste instellingen
2. Start de applicatie: `python3 app.py`
3. Ga naar: http://localhost:5000/settings
4. Klik op "Test Email Verzenden"
5. Voer je eigen email adres in
6. Check je inbox!

---

## ❓ Veelvoorkomende Problemen

### "Authenticatie fout"
- Controleer gebruikersnaam en wachtwoord
- Voor Gmail/Yahoo/iCloud: gebruik een App Password
- Zorg dat 2FA is ingeschakeld waar nodig

### "Server verbinding verbroken"
- Controleer of de SMTP server en poort correct zijn
- Probeer de alternatieve poort (587 → 465 of andersom)
- Check je firewall/antivirus instellingen

### "Connection timeout"
- Controleer je internet verbinding
- Sommige netwerken blokkeren SMTP poorten
- Probeer een andere netwerkverbinding

---

## 💡 Tips

1. **Start met Gmail of Outlook** - deze zijn het makkelijkst te configureren
2. **Gebruik altijd TLS/SSL** - voor beveiliging
3. **Test eerst met je eigen email** - voordat je naar anderen stuurt
4. **Check spam folders** - test emails kunnen daar terechtkomen
5. **Vraag je IT afdeling** - als je bedrijfs email gebruikt

---

## 📝 Voorbeeld .env Bestand

Hier is een compleet voorbeeld voor Outlook:
```env
# Database Configuratie
DATABASE_URL=sqlite:///phishing_simulator.db
SECRET_KEY=change-this-to-random-string

# SMTP Email Configuratie - OUTLOOK
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=jouw-email@outlook.com
SMTP_PASSWORD=jouw-wachtwoord-hier
SMTP_USE_TLS=true
SMTP_USE_SSL=false

# Base URL
BASE_URL=http://localhost:5000

# Flask Configuratie
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

Veel succes! 🚀
