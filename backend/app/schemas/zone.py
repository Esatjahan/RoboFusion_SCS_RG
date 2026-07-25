from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ZoneResponse(BaseModel):
    """Response schema for a monitored campus zone."""

    id: int
    code: str
    name: str
    location: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)