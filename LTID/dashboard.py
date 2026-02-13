"""FastAPI dashboard with WebSocket support for real-time threat intelligence."""
from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from datetime import datetime

from aggregator import ThreatAggregator
from config import Config
from history import ThreatHistory
from lists import ThreatLists
from validators import sanitize_input, is_valid_indicator

# Setup logging - suppress when run from JacOps
import warnings
if os.environ.get('JACOPS_RUNNING') == '1':
    # Suppress all logging when run from JacOps
    logging.basicConfig(level=logging.CRITICAL)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.CRITICAL)
    # Suppress uvicorn and fastapi logging
    logging.getLogger('uvicorn').setLevel(logging.CRITICAL)
    logging.getLogger('uvicorn.access').setLevel(logging.CRITICAL)
    logging.getLogger('fastapi').setLevel(logging.CRITICAL)
    logging.getLogger('collectors').setLevel(logging.CRITICAL)
    # Suppress all warnings
    warnings.filterwarnings("ignore")
else:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# In-memory connections for WebSocket broadcast
active_connections: list[WebSocket] = []
aggregator = ThreatAggregator()
history = ThreatHistory()
threat_lists = ThreatLists()
cached_data: dict | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Background fetcher and cleanup."""
    global cached_data
    cached_data = aggregator.load()
    loop = asyncio.get_event_loop()

    async def fetch_loop():
        global cached_data
        while True:
            try:
                data = await loop.run_in_executor(None, aggregator.fetch_all)
                aggregator.save(data)
                history.save_snapshot(data)
                cached_data = data
                for ws in list(active_connections):
                    try:
                        await ws.send_json(data)
                    except Exception:
                        pass
            except Exception as e:
                logger.error("Fetch loop error: %s", e)
            await asyncio.sleep(Config.POLL_INTERVAL)

    task = asyncio.create_task(fetch_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Threat Intelligence Dashboard", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the dashboard HTML."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(html_path.read_text())


@app.get("/api/data")
async def get_data():
    """REST endpoint for current threat data - always returns immediately."""
    global cached_data
    if cached_data is None:
        # Try to load cached data first
        cached_data = aggregator.load()
        if not cached_data:
            # No cache - return empty state with proper structure
            cached_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "aggregate": {
                    "total_threats": 0,
                    "by_source": {},
                    "by_type": {},
                    "by_country": {},
                    "top_threats": [],
                    "metrics": {},
                },
                "sources": {
                    "abuseipdb": {"count": 0, "threats": []},
                    "otx": {"count": 0, "threats": []},
                    "virustotal": {"count": 0, "threats": []},
                },
            }
        # Always trigger background refresh
        asyncio.create_task(_background_refresh())
    return cached_data


async def _background_refresh():
    """Background refresh without blocking."""
    global cached_data
    loop = asyncio.get_event_loop()
    try:
        new_data = await asyncio.wait_for(
            loop.run_in_executor(None, aggregator.fetch_all),
            timeout=90.0,
        )
        aggregator.save(new_data)
        history.save_snapshot(new_data)
        cached_data = new_data
        # Broadcast to WebSocket clients
        for ws in list(active_connections):
            try:
                await ws.send_json(new_data)
            except Exception:
                pass
    except asyncio.TimeoutError:
        # Timeout - keep existing data or use empty structure
        if cached_data is None:
            cached_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "aggregate": {"total_threats": 0, "by_source": {}, "top_threats": []},
                "sources": {
                    "abuseipdb": {"error": "Timeout bij ophalen data", "count": 0},
                    "otx": {"error": "Timeout bij ophalen data", "count": 0},
                    "virustotal": {"error": "Timeout bij ophalen data", "count": 0},
                },
            }
    except Exception as e:
        # Error - keep existing data or use empty structure with error info
        if cached_data is None:
            cached_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "aggregate": {"total_threats": 0, "by_source": {}, "top_threats": []},
                "sources": {
                    "abuseipdb": {"error": f"Fout: {str(e)[:50]}", "count": 0},
                    "otx": {"error": f"Fout: {str(e)[:50]}", "count": 0},
                    "virustotal": {"error": f"Fout: {str(e)[:50]}", "count": 0},
                },
            }
        logger.error("Background refresh failed: %s", e)


@app.post("/api/refresh")
async def refresh():
    """Trigger immediate data refresh (non-blocking)."""
    global cached_data
    loop = asyncio.get_event_loop()
    try:
        cached_data = await asyncio.wait_for(
            loop.run_in_executor(None, aggregator.fetch_all),
            timeout=90.0,
        )
        aggregator.save(cached_data)
        history.save_snapshot(cached_data)
    except asyncio.TimeoutError:
        logger.warning("Refresh timed out after 90s")
        cached_data = cached_data or {
            "aggregate": {"total_threats": 0, "by_source": {}},
            "sources": {"_timeout": {"error": "Request timed out after 90s"}},
        }
    for ws in list(active_connections):
        try:
            await ws.send_json(cached_data)
        except Exception:
            pass
    return {"status": "ok"}


@app.get("/api/history/timeline")
async def get_timeline(days: int = 7):
    """Get historical timeline data."""
    return {"timeline": history.get_timeline(days=min(days, 30))}


@app.get("/api/history/countries")
async def get_country_trends(days: int = 7):
    """Get country trends over time."""
    return {"trends": history.get_country_trends(days=min(days, 30))}


@app.get("/api/correlations")
async def get_correlations():
    """Get threat correlation data."""
    global cached_data
    if cached_data is None:
        cached_data = aggregator.load()
    correlations = cached_data.get("aggregate", {}).get("correlations", {}) if cached_data else {}
    return correlations


@app.get("/api/lists")
async def get_lists():
    """Get whitelist and blacklist."""
    return threat_lists.get_all()


class IndicatorRequest(BaseModel):
    indicator: str

    @validator("indicator")
    def validate_indicator(cls, v):
        sanitized = sanitize_input(v, max_length=500)
        if not sanitized:
            raise ValueError("Indicator cannot be empty")
        # Basic validation - allow common formats
        if not is_valid_indicator(sanitized, None):
            raise ValueError("Invalid indicator format")
        return sanitized


@app.post("/api/lists/whitelist")
@limiter.limit("10/minute")
async def add_whitelist(request: Request, req: IndicatorRequest):
    """Add indicator to whitelist."""
    threat_lists.add_whitelist(req.indicator)
    return {"status": "ok", "message": f"Added {req.indicator} to whitelist"}


@app.delete("/api/lists/whitelist")
@limiter.limit("10/minute")
async def remove_whitelist(request: Request, req: IndicatorRequest):
    """Remove indicator from whitelist."""
    removed = threat_lists.remove_whitelist(req.indicator)
    return {"status": "ok", "message": f"Removed {req.indicator} from whitelist", "removed": removed}


@app.post("/api/lists/blacklist")
@limiter.limit("10/minute")
async def add_blacklist(request: Request, req: IndicatorRequest):
    """Add indicator to blacklist."""
    threat_lists.add_blacklist(req.indicator)
    return {"status": "ok", "message": f"Added {req.indicator} to blacklist"}


@app.delete("/api/lists/blacklist")
@limiter.limit("10/minute")
async def remove_blacklist(request: Request, req: IndicatorRequest):
    """Remove indicator from blacklist."""
    removed = threat_lists.remove_blacklist(req.indicator)
    return {"status": "ok", "message": f"Removed {req.indicator} from blacklist", "removed": removed}


@app.get("/api/lists/export")
async def export_lists():
    """Export whitelist and blacklist."""
    return threat_lists.get_all()


@app.post("/api/lists/import")
@limiter.limit("5/minute")
async def import_lists(request: Request, data: dict):
    """Import whitelist and blacklist."""
    whitelist = data.get("whitelist", [])
    blacklist = data.get("blacklist", [])
    for ind in whitelist:
        sanitized = sanitize_input(str(ind))
        if is_valid_indicator(sanitized, None):
            threat_lists.add_whitelist(sanitized)
    for ind in blacklist:
        sanitized = sanitize_input(str(ind))
        if is_valid_indicator(sanitized, None):
            threat_lists.add_blacklist(sanitized)
    return {"status": "ok", "imported": {"whitelist": len(whitelist), "blacklist": len(blacklist)}}


@app.get("/api/stats/new-threats")
async def get_new_threats_count():
    """Get count of new threats since last visit (requires client-side timestamp)."""
    # Client sends last_visit timestamp, we compare with current data
    return {"current_total": cached_data.get("aggregate", {}).get("total_threats", 0) if cached_data else 0}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        if cached_data:
            await websocket.send_json(cached_data)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


# Prometheus metrics for Grafana (custom registry to avoid duplicate registration)
try:
    from prometheus_client import CollectorRegistry, Gauge, generate_latest
    from starlette.responses import Response

    _metrics_registry = CollectorRegistry()
    THREAT_COUNT = Gauge(
        "threat_dashboard_total_threats",
        "Total threat count",
        registry=_metrics_registry,
    )
    SOURCE_COUNT = Gauge(
        "threat_dashboard_source_count",
        "Threats per source",
        ["source"],
        registry=_metrics_registry,
    )

    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint for Grafana scraping."""
        if cached_data:
            agg = cached_data.get("aggregate", {})
            THREAT_COUNT.set(agg.get("total_threats", 0))
            for src, count in agg.get("by_source", {}).items():
                SOURCE_COUNT.labels(source=src).set(count)
        return Response(
            content=generate_latest(_metrics_registry),
            media_type="text/plain",
        )
except ImportError:
    pass


# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def run():
    """Run the dashboard server."""
    import uvicorn
    import warnings
    
    # Suppress warnings when run from JacOps
    if os.environ.get('JACOPS_RUNNING') == '1':
        warnings.filterwarnings("ignore")
        # Suppress uvicorn access logs
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "loggers": {
                "uvicorn": {"level": "CRITICAL"},
                "uvicorn.error": {"level": "CRITICAL"},
                "uvicorn.access": {"level": "CRITICAL"},
                "fastapi": {"level": "CRITICAL"},
            },
        }
    else:
        log_config = None
    
    uvicorn.run(
        "dashboard:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=False,
        log_config=log_config,
    )


if __name__ == "__main__":
    run()
