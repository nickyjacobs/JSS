# Grafana Integration

Het threat dashboard exposeert Prometheus metrics op `/metrics`. Grafana kan deze tonen via Prometheus.

## Quick Start (Docker Compose)

1. Start het threat dashboard (op je host, poort 8001):
   ```bash
   python dashboard.py
   ```

2. Start Prometheus + Grafana:
   ```bash
   cd ..
   docker-compose -f docker-compose.grafana.yml up -d
   ```

3. Open Grafana: http://localhost:3000 (login: admin / admin)

4. Voeg Prometheus datasource toe:
   - URL: `http://prometheus:9090`
   - Save & Test

5. Maak een nieuw dashboard met queries:
   - `threat_dashboard_total_threats` - Totaal aantal threats
   - `threat_dashboard_source_count` - Per bron (abuseipdb, otx, virustotal)

## Zonder Docker

1. Installeer Prometheus, voeg aan `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'threat-dashboard'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: /metrics
```

2. Start Prometheus en Grafana lokaal, verbind Grafana met Prometheus.
