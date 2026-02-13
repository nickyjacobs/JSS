# Bijdragen aan JacOps Security Suite

Bedankt dat je wilt bijdragen. Hieronder staan korte richtlijnen.

## Ontwikkelomgeving

1. **Clone de repository**
   ```bash
   git clone https://github.com/nickyjacobs/JSS.git
   cd JSS
   ```

2. **Python**
   - Gebruik Python 3.9 of hoger.
   - Per tool: maak eventueel een venv in de toolmap en installeer `requirements.txt`.

3. **Geen geheimen in de repo**
   - Geen API keys, wachtwoorden of `.env` bestanden committen.
   - Gebruik `.env.example` als voorbeeld en lees echte waarden uit omgeving of `.env` (lokaal, niet gecommit).

## Wijzigingen indienen

1. **Fork** de repo en maak een **branch** voor je wijziging (bijv. `feature/uitbreiding-xyz` of `fix/issue-123`).
2. **Commit** met duidelijke, korte berichten (bijv. `Add IDM .env.example`).
3. **Push** naar je fork en open een **Pull Request** naar de hooftrepo.
4. Beschrijf in de PR wat je hebt gewijzigd en waarom.

## Code-stijl

- Python: volg grotendeels PEP 8 (regelbreedte mag 100 zijn waar nodig).
- Bestaande conventies per toolmap aanhouden (bijv. Nederlands voor gebruikersgericht teksten).

## Documentatie

- Wijzigingen in gedrag of opties: pas [CLI_COMMANDS.md](CLI_COMMANDS.md) en/of de tool-README aan.
- Nieuwe tools of poorten: pas [README.md](README.md) en [PORTS.md](PORTS.md) aan.

## Vragen

Open een **Issue** voor vragen of suggesties.
