from datetime import datetime
from typing import Dict, Any, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class Intent(BaseModel):
    """
    Represents an action proposed by an untrusted agent.
    This object must be strictly validated before any decision is made.
    """

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    entity_id: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    params: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ttl: int = Field(..., gt=0)
