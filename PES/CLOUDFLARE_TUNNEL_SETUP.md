# Cloudflare Tunnel Setup voor Phishing Email Simulator

## Stap 1: Redirect URI in Azure Portal

In je Azure App Registration:

1. Ga naar "Authentication"
2. Klik "+ Add a platform" → "Web" (als je localhost nog hebt, kun je die laten staan voor lokale ontwikkeling)
3. Voeg deze Redirect URI toe:
   ```
   https://jouw-domein.com/auth/callback
   ```
   (Vervang `jouw-domein.com` met je echte Cloudflare domein)

4. Klik "Configure"

**Belangrijk:** Voor productie MOET je HTTPS gebruiken (niet HTTP), behalve voor localhost.

## Stap 2: Cloudflare Tunnel Installeren

### Optie A: cloudflared (Command Line)

1. **Installeer cloudflared:**
   ```bash
   # macOS
   brew install cloudflared
   
   # Of download van: https://github.com/cloudflare/cloudflared/releases
   ```

2. **Login naar Cloudflare:**
   ```bash
   cloudflared tunnel login
   ```
   Dit opent een browser waar je inlogt met je Cloudflare account.

3. **Maak een nieuwe tunnel:**
   ```bash
   cloudflared tunnel create phishing-simulator
   ```

4. **Configureer de tunnel:**
   Maak een configuratie bestand: `~/.cloudflared/config.yml`
   ```yaml
   tunnel: <tunnel-id>
   credentials-file: /Users/nicky/.cloudflared/<tunnel-id>.json
   
   ingress:
     - hostname: phishing.jouw-domein.com
       service: http://localhost:5003
     - service: http_status:404
   ```

5. **Route het domein:**
   ```bash
   cloudflared tunnel route dns phishing-simulator phishing.jouw-domein.com
   ```

6. **Start de tunnel:**
   ```bash
   cloudflared tunnel run phishing-simulator
   ```

### Optie B: Cloudflare Dashboard (Makkelijker)

1. Ga naar: https://dash.cloudflare.com
2. Selecteer je domein
3. Ga naar "Zero Trust" → "Networks" → "Tunnels"
4. Klik "Create a tunnel"
5. Kies "Cloudflared"
6. Geef het een naam: "phishing-simulator"
7. Volg de instructies om de tunnel te installeren en configureren

## Stap 3: Update .env Bestand

Update je `.env` bestand met je productie URL:

```env
# OAuth2 / Microsoft Graph API Configuratie
USE_OAUTH2=true
AZURE_CLIENT_ID=jouw-client-id
AZURE_CLIENT_SECRET=jouw-client-secret
AZURE_TENANT_ID=common
AZURE_REDIRECT_URI=https://jouw-domein.com/auth/callback

# Base URL voor tracking links (productie)
BASE_URL=https://jouw-domein.com

# Flask Configuratie
FLASK_PORT=5003
FLASK_HOST=127.0.0.1  # Alleen lokaal, tunnel zorgt voor externe toegang
```

## Stap 4: Test de Setup

1. Start je applicatie lokaal:
   ```bash
   python3 app.py
   ```

2. Start de Cloudflare tunnel:
   ```bash
   cloudflared tunnel run phishing-simulator
   ```

3. Ga naar: `https://jouw-domein.com`

4. Test OAuth2 login:
   - Klik "Instellingen" → "OAuth2 Login"
   - Log in met je Microsoft account
   - Je zou moeten worden teruggeleid naar je productie URL

## Belangrijke Punten

✅ **HTTPS is verplicht** voor productie (behalve localhost)
✅ **Cloudflare tunnel** zorgt automatisch voor HTTPS
✅ **Lokale app** draait op `localhost:5003`
✅ **Externe toegang** via `https://jouw-domein.com`
✅ **Redirect URI** moet exact overeenkomen met je productie URL

## Troubleshooting

### "Redirect URI mismatch"
- Controleer of de redirect URI in Azure Portal exact overeenkomt
- Zorg dat je HTTPS gebruikt (niet HTTP)
- Controleer of er geen trailing slash is

### Tunnel werkt niet
- Controleer of de tunnel draait: `cloudflared tunnel list`
- Check de tunnel logs voor errors
- Zorg dat je app draait op localhost:5003

### SSL Certificate errors
- Cloudflare tunnel zorgt automatisch voor SSL
- Als je problemen hebt, check je Cloudflare SSL/TLS instellingen
