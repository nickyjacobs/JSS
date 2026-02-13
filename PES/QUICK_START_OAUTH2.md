# Quick Start: OAuth2 Setup

## ✅ Wat is er al gedaan

1. ✅ OAuth2 code is geïmplementeerd
2. ✅ Microsoft Graph API integratie is klaar
3. ✅ Dependencies zijn geïnstalleerd
4. ✅ Client ID is al ingesteld: `cdb1df93-d8e1-4f5a-b6cb-29bb7493fdf7`

## 🔑 Wat je nog moet doen

### Stap 1: Haal je Client Secret op

Je hebt al een App Registration voor n8n. Je kunt dezelfde Client Secret gebruiken of een nieuwe maken:

**Optie A: Bestaande Client Secret gebruiken**
1. Ga naar: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
2. Zoek je App Registration: "n8n-outlook-oauth"
3. Klik erop
4. Ga naar "Certificates & secrets"
5. Als je de secret value niet meer ziet, maak een nieuwe aan (zie Optie B)

**Optie B: Nieuwe Client Secret maken**
1. In je App Registration, ga naar "Certificates & secrets"
2. Klik op "+ New client secret"
3. Beschrijving: "Phishing Simulator"
4. Expiry: 24 months (of langer)
5. Klik "Add"
6. **BELANGRIJK:** Kopieer de secret value direct (je ziet het maar 1x!)

### Stap 2: Controleer API Permissions

1. In je App Registration, ga naar "API permissions"
2. Controleer of `Mail.Send` permission aanwezig is
3. Als niet aanwezig:
   - Klik "+ Add a permission"
   - Selecteer "Microsoft Graph" → "Delegated permissions"
   - Zoek "Mail.Send" en selecteer het
   - Klik "Add permissions"
   - Klik "Grant admin consent" (als nodig)

### Stap 3: Controleer Redirect URI

1. Ga naar "Authentication"
2. Controleer of deze redirect URI bestaat: `http://localhost:5003/auth/callback`
3. Als niet aanwezig:
   - Klik "+ Add a platform" → "Web"
   - Voeg toe: `http://localhost:5003/auth/callback`
   - Klik "Configure"

### Stap 4: Update .env Bestand

Open `/Users/nicky/Desktop/MCST/PES/.env` en update deze regel:

```env
AZURE_CLIENT_SECRET=jouw-client-secret-hier
```

Vervang `jouw-client-secret-hier` met je echte Client Secret.

### Stap 5: Start de Applicatie

```bash
cd /Users/nicky/Desktop/MCST/PES
python3 app.py
```

### Stap 6: OAuth2 Login

1. Ga naar: `http://localhost:5003`
2. Klik op "Instellingen"
3. Klik op "OAuth2 Login"
4. Log in met je Microsoft account (`nicky.jacobs98@outlook.com`)
5. Geef toestemming voor "Mail.Send"
6. Je wordt teruggeleid naar de instellingen pagina

### Stap 7: Test Email Verzenden

1. Op de instellingen pagina, klik "Test Email Verzenden"
2. Voer je email adres in: `nicky.jacobs98@outlook.com`
3. Check je inbox!

## ✅ Klaar!

Als alles werkt, kun je nu:
- Campaigns aanmaken
- Emails versturen via Microsoft Graph API
- Geen problemen meer met "basic authentication disabled"

## Problemen?

- **"Invalid client secret"** → Controleer je Client Secret
- **"Redirect URI mismatch"** → Controleer redirect URI in Azure Portal
- **"Insufficient privileges"** → Controleer Mail.Send permission
- **"Token expired"** → Log opnieuw in via OAuth2 Login

Veel succes! 🚀
