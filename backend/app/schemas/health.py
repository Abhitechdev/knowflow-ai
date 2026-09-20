from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: dict[str, Any]
    auth: dict[str, Any]
    timestamp: str
