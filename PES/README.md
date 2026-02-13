# Phishing Email Simulator

Een volledig werkende tool om realistische phishing emails te genereren en te versturen voor security awareness training. De tool trackt wie op links klikt en verzamelt gedetailleerde statistieken.

## Features

- 🎯 **5 Professionele Phishing Email Templates**:
  - Wachtwoord reset
  - Dringende actie vereist
  - Factuur/payment
  - Beveiligingswaarschuwing
  - Generiek template
- 📊 **Real-time Tracking**: Track clicks, IP adressen, user agents en timestamps
- 📧 **Volledige SMTP Integratie**: Ondersteunt Gmail, Outlook, Yahoo en andere SMTP providers
- 🗄️ **SQLite Database**: Automatische data opslag
- 🌐 **Modern Web Interface**: Intuïtieve UI voor campaign management
- ⚙️ **Configuratie Pagina**: Eenvoudige email instellingen via web interface
- 🧪 **Test Email Functionaliteit**: Test je email configuratie voordat je campaigns verstuurt

## Installatie

1. **Clone of download dit project**

2. **Installeer Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configureer email instellingen:**

   Kopieer `.env.example` naar `.env`:
   ```bash
   cp .env.example .env
   ```

   Bewerk `.env` en vul je SMTP gegevens in:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=jouw-email@gmail.com
   SMTP_PASSWORD=jouw-app-password
   BASE_URL=http://localhost:5000
   ```

   **Voor Gmail:**
   - Je moet een [App Password](https://myaccount.google.com/apppasswords) gebruiken (niet je normale wachtwoord)
   - 2-factor authenticatie moet ingeschakeld zijn
   - Ga naar: https://myaccount.google.com/apppasswords

4. **Start de applicatie:**
```bash
python app.py
```

5. **Open je browser:**
   Ga naar: `http://localhost:5000`

## Gebruik

### 1. Email Configureren

1. Klik op **"Instellingen"** in het menu
2. Vul je SMTP gegevens in
3. Klik op **"Test Email Verzenden"** om te testen
4. Als de test succesvol is, kun je campaigns aanmaken

### 2. Campaign Aanmaken

1. Klik op **"Nieuwe Campaign"**
2. Vul de gegevens in:
   - Campaign naam
   - Email onderwerp
   - Afzender naam en email
   - Template type
   - Ontvangers (één per regel)
3. Klik op **"Campaign Aanmaken"**

### 3. Emails Versturen

1. Ga naar de campaign detail pagina
2. Klik op **"Emails Versturen"**
3. De applicatie verstuurt emails naar alle ontvangers
4. Bekijk real-time statistieken

### 4. Resultaten Bekijken

- **Statistieken**: Totaal ontvangers, clicks, click rate
- **Click Geschiedenis**: Wie heeft geklikt, wanneer, IP adres, user agent
- **Ontvangers Overzicht**: Status van elke ontvanger

## SMTP Providers

### Gmail
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
```
**Belangrijk:** Gebruik een App Password, niet je normale wachtwoord!

### Outlook/Hotmail
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

### Yahoo
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

### Andere Providers
Raadpleeg de documentatie van je email provider voor de juiste SMTP instellingen.

## Database

De applicatie gebruikt SQLite en maakt automatisch een `phishing_simulator.db` bestand aan bij de eerste run. Alle data wordt hierin opgeslagen:
- Campaigns
- Recipients
- Click tracking data

## Base URL Configuratie

Voor productie gebruik moet je `BASE_URL` instellen naar je publieke domein:
```env
BASE_URL=https://jouw-domein.com
```

Dit is nodig zodat tracking links correct werken wanneer ontvangers op links klikken.

## Beveiliging

⚠️ **BELANGRIJK:** Deze tool is alleen bedoeld voor legitieme security awareness training binnen je eigen organisatie. 

**Gebruik deze tool NIET voor:**
- Illegale activiteiten
- Phishing buiten je eigen organisatie
- Zonder expliciete toestemming van de ontvangers
- Malicious doeleinden

**Best Practices:**
- Gebruik alleen binnen je eigen organisatie
- Informeer medewerkers over security awareness training
- Gebruik de resultaten om training te verbeteren, niet om te straffen
- Bewaar gevoelige data veilig

## Troubleshooting

### Emails worden niet verzonden

1. **Check je SMTP configuratie:**
   - Ga naar Instellingen
   - Controleer of alle velden correct zijn ingevuld
   - Gebruik "Test Email Verzenden" om te testen

2. **Gmail specifiek:**
   - Zorg dat je een App Password gebruikt
   - Controleer dat 2FA is ingeschakeld
   - Mogelijk moet je "Minder veilige apps" toestaan (oude accounts)

3. **Firewall/Netwerk:**
   - Controleer of poort 587 of 465 niet geblokkeerd is
   - Sommige netwerken blokkeren SMTP verkeer

### Tracking links werken niet

- Zorg dat `BASE_URL` correct is ingesteld
- Voor lokale ontwikkeling: gebruik `http://localhost:5000`
- Voor productie: gebruik je publieke domein met `https://`

### Database errors

- Verwijder `phishing_simulator.db` en start de applicatie opnieuw
- De database wordt automatisch opnieuw aangemaakt

## Technische Details

- **Backend**: Flask (Python)
- **Database**: SQLite met SQLAlchemy ORM
- **Email**: SMTP met TLS/SSL ondersteuning
- **Frontend**: HTML/CSS/JavaScript
- **Templates**: Jinja2

## Licentie

Voor intern gebruik alleen.

## Support

Voor vragen of problemen, check de troubleshooting sectie of raadpleeg de code documentatie.
