from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100)

class WorkspaceRead(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
