# Contributing to Password Policy Analyzer

Bedankt voor je interesse in het bijdragen aan het Password Policy Analyzer project!

## Code Style

- Gebruik Python type hints waar mogelijk
- Volg PEP 8 style guide
- Voeg docstrings toe aan alle functies en classes
- Gebruik betekenisvolle variabele namen

## Testing

Voordat je een pull request indient, test je code lokaal:

```bash
# Start de applicatie
./run.sh

# Test de API endpoints
curl -X POST http://localhost:5500/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"min_length": 8, "lang": "nl"}'
```

## Policy Checks

Bij het toevoegen van nieuwe policy checks:

1. Voeg de check toe aan `PolicyAnalyzer.analyze()`
2. Voeg translations toe voor beide talen (nl/en)
3. Gebruik de juiste severity level:
   - CRITICAL: Directe beveiligingsrisico's
   - HIGH: Belangrijke beveiligingsproblemen
   - MEDIUM: Aanbevolen verbeteringen
   - LOW: Best practices met lagere prioriteit
4. Voeg breach statistics toe waar relevant
5. Update de README met de nieuwe check

## Pull Request Process

1. Maak een duidelijke beschrijving van je wijzigingen
2. Zorg dat alle tests slagen
3. Update documentatie waar nodig
4. Voeg screenshots toe voor UI wijzigingen

## Questions?

Als je vragen hebt, open een issue op GitHub.
