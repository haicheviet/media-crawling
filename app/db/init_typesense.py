import typesense
from app.core.config import settings

client = typesense.Client(
        {
            "api_key": settings.TYPESENSE_KEY,
            "nodes": [{"host": settings.TYPESENSE_HOST, "port": settings.TYPESENSE_PORT, "protocol": "http"}],
            "connection_timeout_seconds": 120,
        }
    )