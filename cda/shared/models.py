from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class Intent(BaseModel):
    """
    Represents an action proposed by an untrusted agent.
    frozen=True ensures the intent cannot be modified after creation.
    """
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    entity_id: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    params: Dict[str, Any] = Field(default_factory=dict)
    # Using timezone-aware UTC now for Python 3.12 compatibility
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ttl: int = Field(default=300, gt=0)

class ContextSnapshot(BaseModel):
    """
    Verified state provided by a trusted Context Provider.
    """
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    entity_id: str
    state: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))