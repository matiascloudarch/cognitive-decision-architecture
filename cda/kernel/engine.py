"""
Cognitive Decision Architecture (CDA) - Core Kernel Engine
Provides policy evaluation, PASETO v4 token generation, and forensic ledger tracking.
"""

import os
import uuid
import datetime
import hashlib
import json
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
import pyseto
from pyseto import Key

app = FastAPI(
    title="Cognitive Decision Architecture - Kernel",
    version="1.0.0",
    description="Deterministic runtime control plane and forensic ledger."
)

# Shared local symmetric key for PASETO v4 (32 bytes / 64 hex chars)
# Matches exactly the Gate configuration
SECRET_HEX = os.getenv(
    "CDA_SECRET_HEX", 
    "707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f"
)
PASETO_KEY = Key.new(version=4, purpose="local", key=bytes.fromhex(SECRET_HEX))

# Mock database records
MOCK_USER_DB = {
    "usr_001": {
        "status": "ACTIVE",
        "kyc_status": "VERIFIED",
        "risk_score": 0.05,
        "verified": True
    }
}

MOCK_POLICIES = {
    "FINRA_US": {
        "auto_approve_limit": 500.0,
        "remediate_limit": 1000.0,
        "escalate_limit": 1000.0,
        "max_limit": 10000.0
    },
    "ISO_42001": {
        "auto_approve_limit": 500.0,
        "remediate_limit": 1000.0,
        "escalate_limit": 1000.0,
        "max_limit": 10000.0
    }
}


class AgentIntent(BaseModel):
    entity_id: str = Field(..., json_schema_extra={"example": "usr_001"})
    agent_id: str = Field(..., json_schema_extra={"example": "agent-007"})
    action: str = Field(..., json_schema_extra={"example": "transfer_funds"})
    params: Dict[str, Any] = Field(default_factory=dict)
    regime_context: Optional[str] = Field("FINRA_US", json_schema_extra={"example": "FINRA_US"})
    jurisdiction: Optional[str] = Field("US", json_schema_extra={"example": "US"})
    principal_authority_id: Optional[str] = None


class EvaluatedCheck(BaseModel):
    check_id: str
    version_hash: str
    status: str
    rationale: str


class BypassedCheck(BaseModel):
    check_id: str
    rationale: str


class AuditDecision(BaseModel):
    verdict: str
    paseto_token: Optional[str] = None
    drift_index: float
    principal_authority_id: str
    regime_context: str
    jurisdiction: str
    evaluated_checks: List[EvaluatedCheck]
    bypassed_checks: List[BypassedCheck]
    decision_reason: str


def compute_sha256(data: Any) -> str:
    """Compute SHA-256 hash for deterministic audit trails."""
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@app.post("/authorize", response_model=AuditDecision)
def authorize_intent(
    intent: AgentIntent,
    human_signature: Optional[str] = Query(None)
) -> AuditDecision:
    """
    Evaluates an agent intent against defined governance policy limits.
    """
    user_data = MOCK_USER_DB.get(intent.entity_id)
    policy = MOCK_POLICIES.get(intent.regime_context, MOCK_POLICIES["FINRA_US"]).copy()

    # Fallback default policy hash
    policy_hash = compute_sha256(policy)

    if not user_data:
        return AuditDecision(
            verdict="BLOCK",
            paseto_token=None,
            drift_index=1.0,
            principal_authority_id=intent.principal_authority_id or "UNKNOWN",
            regime_context=intent.regime_context or "UNKNOWN",
            jurisdiction=intent.jurisdiction or "UNKNOWN",
            evaluated_checks=[
                EvaluatedCheck(
                    check_id="POL-ID-01",
                    version_hash=policy_hash,
                    status="FAILED",
                    rationale="Entity ID not recognized in authority database"
                )
            ],
            bypassed_checks=[],
            decision_reason="Unknown entity_id provided"
        )

    # Policy boundary enforce
    if intent.action == "transfer_funds":
        policy["auto_approve_limit"] = 500.0
        policy["remediate_limit"] = 1000.0
        policy["escalate_limit"] = 1000.0
        policy["max_limit"] = 10000.0

    amount = float(intent.params.get("amount", 0.0))
    principal_id = (
        intent.principal_authority_id
        or f"{intent.entity_id}->tenant_{intent.jurisdiction.lower()}->{intent.agent_id}"
    )
    regime = intent.regime_context or "FINRA_US"
    jurisdiction = intent.jurisdiction or "US"

    auto_limit = policy["auto_approve_limit"]
    max_limit = policy["max_limit"]

    denominator = max_limit - auto_limit if max_limit > auto_limit else 1.0
    drift_index = round(min(1.0, max(0.0, (amount - auto_limit) / denominator)), 2)

    evaluated_checks: List[EvaluatedCheck] = []
    bypassed_checks: List[BypassedCheck] = []

    evaluated_checks.append(
        EvaluatedCheck(
            check_id="POL-ID-01",
            version_hash=policy_hash,
            status="PASSED" if user_data.get("verified") else "FAILED",
            rationale="User identity verified in secure registry"
        )
    )

    verdict = "PERMIT"
    decision_reason = "Intent matches policy guidelines"
    adjusted_amount = amount

    # Evaluation logic based on transaction limits
    if amount > policy["max_limit"]:
        verdict = "BLOCK"
        decision_reason = f"Amount ${amount} exceeds maximum policy boundary of ${policy['max_limit']}"
        evaluated_checks.append(
            EvaluatedCheck(
                check_id="POL-LIMIT-MAX",
                version_hash=policy_hash,
                status="FAILED",
                rationale=decision_reason
            )
        )
    elif amount > policy["escalate_limit"]:
        if human_signature:
            verdict = "PERMIT"
            decision_reason = f"Amount ${amount} approved via Human-in-the-Loop signature ({human_signature})"
            evaluated_checks.append(
                EvaluatedCheck(
                    check_id="POL-HITL-01",
                    version_hash=policy_hash,
                    status="PASSED",
                    rationale=decision_reason
                )
            )
        else:
            verdict = "ESCALATE"
            decision_reason = f"Amount ${amount} requires Human-in-the-Loop authorization"
            evaluated_checks.append(
                EvaluatedCheck(
                    check_id="POL-HITL-01",
                    version_hash=policy_hash,
                    status="WARNED",
                    rationale=decision_reason
                )
            )
    elif amount > policy["auto_approve_limit"] and amount <= policy["remediate_limit"]:
        verdict = "REMEDIATE"
        adjusted_amount = policy["auto_approve_limit"]
        decision_reason = f"Amount ${amount} automatically capped to approved limit of ${adjusted_amount}"
        evaluated_checks.append(
            EvaluatedCheck(
                check_id="POL-REMED-01",
                version_hash=policy_hash,
                status="PASSED",
                rationale=decision_reason
            )
        )
    else:
        evaluated_checks.append(
            EvaluatedCheck(
                check_id="POL-LIMIT-AUTO",
                version_hash=policy_hash,
                status="PASSED",
                rationale="Amount within automated execution boundary"
            )
        )

    # Issue cryptographic token for executable verdicts
    paseto_token = None
    if verdict in ["PERMIT", "REMEDIATE"]:
        now = datetime.datetime.now(datetime.timezone.utc)
        intent_id = str(uuid.uuid4())
        
        # Include all mandatory fields for Gate's database
        payload = {
            "intent_id": intent_id,
            "sub": intent.entity_id,
            "agent_id": intent.agent_id,
            "action": intent.action,
            "params": {"amount": adjusted_amount},
            "amount": adjusted_amount,
            "verdict": verdict,
            "principal_authority_id": principal_id,
            "regime_context": regime,
            "jurisdiction": jurisdiction,
            "approval_type": "HITL" if human_signature else "AUTO",
            "human_auditor": human_signature,
            "policy_version": policy_hash,
            "execution_graph_hash": policy_hash,
            "issued_at": now.isoformat(),
            "receipt_hash": compute_sha256({"id": intent_id, "verdict": verdict}),
            "iat": now.isoformat(),
            "exp": (now + datetime.timedelta(minutes=15)).isoformat()
        }
        
        # Serialize payload to JSON bytes for PASETO v4 encoding
        serialized_payload = json.dumps(payload).encode("utf-8")
        token_bytes = pyseto.encode(PASETO_KEY, serialized_payload)
        paseto_token = token_bytes.decode("utf-8")

    return AuditDecision(
        verdict=verdict,
        paseto_token=paseto_token,
        drift_index=drift_index,
        principal_authority_id=principal_id,
        regime_context=regime,
        jurisdiction=jurisdiction,
        evaluated_checks=evaluated_checks,
        bypassed_checks=bypassed_checks,
        decision_reason=decision_reason
    )