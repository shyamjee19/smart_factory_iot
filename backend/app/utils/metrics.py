from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge

# Custom metrics (Instrumentator handles standard API metrics automatically)
active_connections = Gauge('websocket_active_connections', 'Number of active WebSocket connections')
messages_sent = Counter('websocket_messages_sent_total', 'Total number of messages sent via WebSocket')

def setup_metrics(app):
    """Initialize Prometheus metrics for the FastAPI app."""
    # Instrument the app and expose the /metrics endpoint
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=[".*admin.*", "/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="inprogress",
        inprogress_labels=True,
    ).instrument(app).expose(app, include_in_schema=False)
