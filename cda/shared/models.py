from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class Intent(BaseModel):
    """Action proposed by the AI Agent."""
    model_config = ConfigDict(frozen=True)
    id: UUID = Field(default_factory=uuid4)
    entity_id: str = Field(...)
    agent_id: str = Field(...)
    action: str = Field(...)
    params: Dict[str, Any] = Field(default_factory=dict)
    # The agent might try to send a context, but we will ignore it 
    # and fetch our own in the Kernel for real auditing.

class AuditDecision(BaseModel):
    """Decision made by the Kernel."""
    intent_id: UUID
    decision: str  # ALLOW, DENY, ESCALATE_TO_HUMAN
    reason: str
    paseto_token: Optional[str] = None
    requires_human_signature: bool = False

# --- TRUSTED SOURCE OF TRUTH (Mock Database) ---
MOCK_USER_DB = {
    "user-001": {"balance": 1200.0, "role": "vip", "verified": True},
    "user-99": {"balance": 100.0, "role": "standard", "verified": True}
}

# --- BUSINESS POLICIES (Deterministic Rules) ---
MOCK_POLICIES = {
    "transfer_funds": {
        "auto_approve_limit": 500.0, # Under this, AI can do it alone
        "max_limit": 2000.0,         # Absolute max
        "require_human_above": 500.0 # Above this, we need a human
    }
}