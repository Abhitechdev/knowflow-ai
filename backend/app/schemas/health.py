from typing import Any, Dict
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: Dict[str, Any]
    auth: Dict[str, Any]
    timestamp: str
