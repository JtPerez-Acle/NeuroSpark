"""Monitoring and metrics collection."""
from prometheus_client import Counter, Histogram, Gauge
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

# HTTP request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Database metrics
db_operations_total = Counter(
    'database_operations_total',
    'Total number of database operations',
    ['operation', 'status']
)

db_operations_duration_seconds = Histogram(
    'database_operations_duration_seconds',
    'Database operation duration in seconds',
    ['operation']
)

# WebSocket metrics
websocket_connections_total = Counter(
    'websocket_connections_total',
    'Total number of WebSocket connections',
    ['status']  # connected, disconnected
)

websocket_messages_total = Counter(
    'websocket_messages_total',
    'Total number of WebSocket messages',
    ['direction', 'type']  # direction: sent/received, type: message type
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP request metrics."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and collect metrics."""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record metrics
            endpoint = request.url.path
            method = request.method
            status_code = response.status_code
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error metrics
            endpoint = request.url.path
            method = request.method
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            raise

def instrument_app(app: FastAPI):
    """Add metrics instrumentation to the FastAPI app."""
    app.add_middleware(MetricsMiddleware)
    
    # Add metrics endpoint
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    @app.get("/metrics")
    async def metrics():
        """Endpoint for exposing metrics."""
        return Response(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )