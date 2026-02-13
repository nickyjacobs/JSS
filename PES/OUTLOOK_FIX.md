# Outlook Basic Authentication Probleem Oplossen

## Het Probleem

Je krijgt de fout: "Authentication unsuccessful, basic authentication is disabled"

Dit betekent dat Microsoft basic authentication heeft uitgeschakeld voor je account.

## Oplossing: Basic Authentication Inschakelen

### Stap 1: Ga naar Microsoft Account Security

1. Ga naar: https://account.microsoft.com/security
2. Log in met je Outlook account: `nicky.jacobs98@outlook.com`

### Stap 2: Zoek naar "App passwords" of "App-wachtwoorden"

1. Scroll naar beneden naar "App passwords" sectie
2. Als je dit niet ziet, probeer:
   - https://account.microsoft.com/security/app-passwords
   - Of zoek in de security instellingen naar "App passwords"

### Stap 3: Controleer of Basic Authentication is ingeschakeld

Soms moet je eerst basic authentication inschakelen voordat App Passwords werken:

1. Ga naar: https://account.live.com/ManageSecurity
2. Zoek naar "Basic authentication" of "Less secure app access"
3. Zet dit AAN (als het er is)

### Stap 4: Maak een Nieuw App Password

1. Ga terug naar App passwords
2. Klik op "Create a new app password"
3. Geef het een naam: "Phishing Simulator"
4. Kopieer het nieuwe App Password EXACT (zonder spaties)
5. Update je `.env` bestand

## Alternatieve Oplossing: OAuth2

Als basic authentication niet beschikbaar is, moet je mogelijk OAuth2 gebruiken. Dit is complexer maar wel mogelijk.

## Huidige Configuratie

Je `.env` bestand is ingesteld met:
- Email: nicky.jacobs98@outlook.com
- App Password: uylrrygrfcawotrh
- Server: smtp-mail.outlook.com
- Poort: 587

De configuratie ziet er correct uit, maar Microsoft blokkeert basic authentication voor je account.
