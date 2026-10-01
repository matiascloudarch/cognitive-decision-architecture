# cda/shared/models.py
# Cognitive Decision Architecture - Shared Governance Models & Mock Registries

import uuid
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field

VerdictType = Literal["PERMIT", "REMEDIATE", "ESCALATE", "BLOCK", "INDETERMINATE"]


class Intent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str
    agent_id: str
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)
    principal_authority_id: Optional[str] = None
    regime_context: Optional[str] = "FINRA_US"
    jurisdiction: Optional[str] = "US"


class EvaluatedCheck(BaseModel):
    check_id: str
    version_hash: str
    status: Literal["PASSED", "FAILED", "WARNED"]
    rationale: str


class BypassedCheck(BaseModel):
    check_id: str
    bypass_reason: str


class AttestedPath(BaseModel):
    evaluated_checks: List[EvaluatedCheck] = Field(default_factory=list)
    bypassed_checks: List[BypassedCheck] = Field(default_factory=list)
    execution_graph_hash: str


class AuditDecision(BaseModel):
    intent_id: str
    verdict: VerdictType
    reason: str
    principal_authority_id: str
    regime_context: str
    jurisdiction: str
    stochastic_drift_index: float
    attested_path: Optional[AttestedPath] = None
    paseto_token: Optional[str] = None
    requires_human_signature: bool = False


# Trusted Governance Registries
MOCK_USER_DB: Dict[str, Dict[str, Any]] = {
    "usr_001": {
        "name": "Alice Corp Admin",
        "role": "treasury_operator",
        "verified": True,
        "allowed_actions": ["transfer_funds", "execute_trade", "update_policy"]
    },
    "usr_002": {
        "name": "Bob Restricted User",
        "role": "read_only",
        "verified": True,
        "allowed_actions": ["view_balance"]
    }
}

MOCK_POLICIES: Dict[str, Dict[str, Any]] = {
    "transfer_funds": {
        "auto_approve_limit": 500.0,
        "remediate_limit": 1000.0,
        "escalate_limit": 5000.0,
        "max_limit": 10000.0,
        "allowed_jurisdictions": ["US", "EU", "CL"]
    },
    "execute_trade": {
        "auto_approve_limit": 1000.0,
        "remediate_limit": 2000.0,
        "escalate_limit": 10000.0,
        "max_limit": 50000.0,
        "allowed_jurisdictions": ["US"]
    }
}