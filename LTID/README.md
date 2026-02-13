# Live Cybersecurity Threat Dashboard

Real-time threat intelligence dashboard dat data aggregeert van **AbuseIPDB**, **AlienVault OTX** en **VirusTotal**. Python voor data processing, modern web dashboard met real-time visualisaties.

## Features

### Core Functionality
- **Multi-source aggregation**: AbuseIPDB blacklist, AlienVault OTX pulses, VirusTotal IP checks
- **Real-time updates**: WebSocket updates elke poll-interval
- **Historical tracking**: 7-day threat timeline en country trends
- **Whitelist/Blacklist**: Export/import functionaliteit voor threat management

### Advanced Threat Intelligence
- **Risk Scoring**: Gecombineerde risk score (0-100) per indicator op basis van:
  - Source reliability (multi-source bonus)
  - Recency (recentere threats = hogere score)
  - Threat type severity
  - VirusTotal malicious/suspicious counts
  - OTX tags (malware, C2, botnet, etc.)
- **Threat Correlation**: Automatische detectie van gerelateerde threats:
  - Same domain/hostname patterns
  - Same country
  - Same tags/pulses
- **Threat Actor Attribution**: Detectie van bekende threat actors (APT28, APT29, Lazarus, Emotet, Mirai, Conti, LockBit)
- **Threat Velocity**: Analyse van threat snelheid (threats per uur, peak hours, trends)
- **Severity Distribution**: Visualisatie van threat severity levels (Critical, High, Medium, Low, Info)

### Visualizations
- **Interactive World Map**: Country heatmap met click-to-zoom functionaliteit
- **Charts**: 
  - Threats by Source (doughnut)
  - Threats by Type (doughnut)
  - Threats by Country (bar)
  - Threat Timeline 7 days (line)
  - Threat Severity Distribution (doughnut)
  - Threat Velocity (bar - 24 hour distribution)
  - OTX Tags (horizontal bar)
- **Top Threats Table**: Sorteerbare tabel met risk scores, severity, threat actors, en multi-source indicators

### Security & Quality
- **Input Validation**: Sanitization en validatie van alle inputs
- **Rate Limiting**: API rate limiting ter bescherming
- **CORS**: Configureerbare CORS settings
- **Duplicate Detection**: Automatische detectie en verwijdering van duplicate threats
- **Data Quality**: Validatie van indicators en country detection

### Grafana Integration
- Prometheus metrics endpoint (`/metrics`) voor Grafana integratie
- Historical data export voor trend analysis

## Installatie

```bash
# Virtual environment (aanbevolen)
python -m venv venv
source venv/bin/activate   # Linux/macOS
# of: venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

## API Keys

1. Kopieer `.env.example` naar `.env`:
   ```bash
   cp .env.example .env
   ```

2. Vul je API keys in `.env`:
   - **AbuseIPDB**: https://www.abuseipdb.com/account/register (gratis 1000 req/dag)
   - **AlienVault OTX**: https://otx.alienvault.com/api (gratis, account vereist)
   - **VirusTotal**: https://www.virustotal.com/gui/my-apikey (gratis 4 req/min)

3. **OTX tip**: Abonneer je op public pulses op https://otx.alienvault.com voor data in het dashboard.

## Starten

```bash
# Start dashboard (standaard op http://localhost:8001)
python dashboard.py

# Of met uvicorn direct:
uvicorn dashboard:app --host 0.0.0.0 --port 8001
```

## Configuratie (.env)

| Variabele | Default | Beschrijving |
|-----------|---------|--------------|
| ABUSEIPDB_API_KEY | - | AbuseIPDB API key |
| OTX_API_KEY | - | AlienVault OTX API key |
| VIRUSTOTAL_API_KEY | - | VirusTotal API key |
| DASHBOARD_HOST | 0.0.0.0 | Bind host |
| DASHBOARD_PORT | 8001 | Poort |
| POLL_INTERVAL_SECONDS | 300 | Interval (sec) tussen API fetches |

## Structuur

```
LTID/
├── collectors/              # API collectors
│   ├── abuseipdb.py        # AbuseIPDB blacklist + check
│   ├── otx.py              # AlienVault OTX pulses
│   └── virustotal.py       # VirusTotal IP/domain lookup
├── aggregator.py           # Aggregatie + opslag
├── dashboard.py            # FastAPI + WebSocket server
├── config.py               # Configuratie
├── history.py              # Historical data management
├── lists.py                # Whitelist/Blacklist management
├── validators.py           # Input validation & sanitization
├── threat_scoring.py       # Risk scoring & severity calculation
├── threat_intelligence.py  # Threat correlation & actor attribution
├── static/                 # Web dashboard UI
│   └── index.html
├── data/                   # Cached threat data (JSON)
│   └── history/           # Historical snapshots
├── grafana/                # Grafana/Prometheus integratie
└── requirements.txt
```

## API Endpoints

- `GET /` - Dashboard UI
- `GET /api/data` - Get current threat data
- `POST /api/refresh` - Manually trigger data refresh
- `GET /api/history/timeline?days=7` - Get historical timeline
- `GET /api/history/countries?days=7` - Get country trends
- `GET /api/correlations` - Get threat correlation data
- `GET /api/lists` - Get whitelist/blacklist
- `POST /api/lists/export` - Export threat lists
- `POST /api/lists/import` - Import threat lists
- `POST /api/lists/whitelist` - Add to whitelist
- `POST /api/lists/blacklist` - Add to blacklist
- `DELETE /api/lists/whitelist/{indicator}` - Remove from whitelist
- `DELETE /api/lists/blacklist/{indicator}` - Remove from blacklist
- `GET /metrics` - Prometheus metrics
- `WebSocket /ws` - Real-time updates

## Grafana

Het dashboard exposeert Prometheus metrics op `/metrics`. Zie `grafana/README.md` voor Grafana setup.

```bash
curl http://localhost:8001/metrics
```

## Licentie

MIT
