# Azure OAuth2 Setup Gids

## Stap 1: Azure App Registration

Je hebt al een App Registration voor n8n! We kunnen die gebruiken of een nieuwe maken.

### Optie A: Bestaande App Registration Gebruiken

Als je dezelfde App Registration wilt gebruiken als n8n:
- Client ID: `cdb1df93-d8e1-4f5a-b6cb-29bb7493fdf7`
- Client Secret: (je hebt deze al in n8n)

### Optie B: Nieuwe App Registration Maken

1. Ga naar: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
2. Klik op "+ New registration"
3. Geef het een naam: "Phishing Email Simulator"
4. Selecteer "Accounts in any organizational directory and personal Microsoft accounts"
5. Klik op "Register"

## Stap 2: API Permissions Configureren

1. Ga naar je App Registration
2. Klik op "API permissions"
3. Klik op "+ Add a permission"
4. Selecteer "Microsoft Graph"
5. Selecteer "Delegated permissions"
6. Zoek en selecteer: `Mail.Send`
7. Klik op "Add permissions"
8. Klik op "Grant admin consent" (als je admin bent)

## Stap 3: Client Secret Maken

1. Ga naar "Certificates & secrets"
2. Klik op "+ New client secret"
3. Geef het een beschrijving: "Phishing Simulator"
4. Kies expiry (bijv. 24 months)
5. Klik op "Add"
6. **BELANGRIJK:** Kopieer de secret value direct (je ziet het maar 1x!)

## Stap 4: Redirect URI Configureren

1. Ga naar "Authentication"
2. Klik op "+ Add a platform"
3. Selecteer "Web"
4. Voeg redirect URI toe: `http://localhost:5003/auth/callback`
5. Klik op "Configure"

## Stap 5: .env Bestand Updaten

Voeg deze regels toe aan je `.env` bestand:

```env
# OAuth2 / Microsoft Graph API
USE_OAUTH2=true
AZURE_CLIENT_ID=cdb1df93-d8e1-4f5a-b6cb-29bb7493fdf7
AZURE_CLIENT_SECRET=jouw-client-secret-hier
AZURE_TENANT_ID=common
AZURE_REDIRECT_URI=http://localhost:5003/auth/callback
```

**Voor personal Microsoft accounts gebruik je:**
- `AZURE_TENANT_ID=common`

**Voor bedrijfs accounts gebruik je:**
- Je tenant ID (te vinden in Azure Portal → Azure Active Directory → Overview)

## Stap 6: Dependencies Installeren

```bash
pip3 install -r requirements.txt
```

## Stap 7: Applicatie Starten en Testen

1. Start de applicatie: `python3 app.py`
2. Ga naar: `http://localhost:5003`
3. Klik op "Instellingen"
4. Klik op "OAuth2 Login" (als je OAuth2 hebt ingeschakeld)
5. Log in met je Microsoft account
6. Test email verzenden

## Troubleshooting

### "Invalid client secret"
- Controleer of je de Client Secret correct hebt gekopieerd
- Zorg dat er geen extra spaties zijn

### "Redirect URI mismatch"
- Controleer of de redirect URI in Azure Portal exact overeenkomt met `AZURE_REDIRECT_URI` in je `.env`
- Voor localhost: `http://localhost:5003/auth/callback`
- Voor productie: `https://jouw-domein.com/auth/callback`

### "Insufficient privileges"
- Controleer of `Mail.Send` permission is toegevoegd
- Controleer of admin consent is gegeven (voor bedrijfs accounts)

### "Token expired"
- OAuth2 tokens verlopen na een bepaalde tijd
- Log opnieuw in via `/auth/login`

## Voordelen van OAuth2

✅ Werkt met moderne Microsoft accounts (geen basic auth nodig)
✅ Veiliger dan App Passwords
✅ Werkt met zowel personal als bedrijfs accounts
✅ Geen problemen met "basic authentication disabled"
