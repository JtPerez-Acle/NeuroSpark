"""Prometheus metrics configuration for the KQML Parser Backend."""
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator, metrics

# Custom metrics
KQML_MESSAGES = Counter(
    "kqml_messages_total",
    "Total number of KQML messages processed",
    ["performative", "status"]
)

DB_OPERATIONS = Histogram(
    "database_operation_duration_seconds",
    "Duration of database operations",
    ["operation", "status"],
    buckets=(0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

WS_CONNECTIONS = Counter(
    "websocket_connections_total",
    "Total WebSocket connections",
    ["status"]
)

def instrument_app(app):
    """Initialize Prometheus metrics instrumentation."""
    Instrumentator().instrument(app).expose(app)

    # Add custom metrics
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        response = await call_next(request)
        
        # Track WebSocket connections
        if request.url.path == "/ws":
            WS_CONNECTIONS.labels(
                status="success" if response.status_code == 101 else "failed"
            ).inc()
            
        return response