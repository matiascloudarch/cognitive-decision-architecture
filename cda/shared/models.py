# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

"""
Cognitive Decision Architecture (CDA 2.0)
Module: cda.shared.models
"""

import uuid
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

# Defined Verdict Types for Axis 1
VerdictType = Literal["PERMIT", "REMEDIATE", "ESCALATE", "INDETERMINATE", "BLOCK"]

# Defined Execution Status Types for Axis 2
ExecutionStatusType = Literal[
    "COMPLETE",
    "UNMAPPED_REGIME_CONTEXT",
    "INVALID_REGIME_CONTEXT",
    "INVALID_TOKEN",
    "EXPIRED_LEASE",
    "UNRESOLVED_DEPENDENCY_OR_STALE_CONTEXT",
    "INTERNAL_EVALUATION_ERROR",
]


class RemediationDetails(BaseModel):
    """Preserves original intent, remediated intent, and rule authority for REMEDIATE verdicts."""

    rule_id: Optional[str] = None
    original_payload: dict[str, Any] = Field(
        default_factory=dict, description="Original input intent parameters before remediation"
    )
    adjusted_payload: dict[str, Any] = Field(
        default_factory=dict, description="Adjusted intent parameters enforced by policy"
    )
    justification: Optional[str] = None
    remediation_authority: Optional[str] = Field(
        None, description="Policy rule ID forcing the remediation"
    )


class Axis1ActionVerdict(BaseModel):
    """Axis 1: Decision on the requested operational action."""

    state: VerdictType = Field(
        ..., description="Action verdict state: PERMIT, REMEDIATE, ESCALATE, INDETERMINATE, BLOCK"
    )
    fallback_action: Optional[Literal["BLOCK"]] = Field(
        None, description="Enforced fallback action when verdict is INDETERMINATE or BLOCK"
    )
    remediation_details: Optional[RemediationDetails] = Field(
        None, description="Mandatory details preserved when state is REMEDIATE"
    )


class Axis2EvaluationEvidence(BaseModel):
    """Axis 2: Attestation evidence regarding the completeness and validity of the evaluation itself."""

    execution_status: ExecutionStatusType = Field(
        ..., description="Status of the policy evaluation engine execution"
    )
    checks_executed: list[str] = Field(
        default_factory=list, description="List of check IDs actually executed"
    )
    failure_mode: Optional[str] = Field(
        None, description="Specific failure mode code (e.g., SF-003, INVALID_REGIME_CONTEXT)"
    )


class AgentIntent(BaseModel):
    """Operational action request dispatched by an autonomous AI agent."""

    intent_id: str = Field(default_factory=lambda: f"int_{uuid.uuid4().hex[:8]}")
    entity_id: str = Field(..., json_schema_extra={"example": "usr_001"})
    agent_id: str = Field(..., json_schema_extra={"example": "agent-007"})
    action: str = Field(..., json_schema_extra={"example": "transfer_funds"})
    params: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    principal_authority_id: Optional[str] = None
    regime_context: Optional[str] = Field("FINRA_US", json_schema_extra={"example": "FINRA_US"})
    jurisdiction: Optional[str] = Field("US", json_schema_extra={"example": "US"})


class EvaluatedCheck(BaseModel):
    """Granular rule execution record emitted during evaluation."""

    check_id: str
    rule_name: str
    passed: bool
    details: str
    status: Optional[str] = None
    rationale: Optional[str] = None
    version_hash: Optional[str] = None


class AuditDecision(BaseModel):
    """External API response contract summarizing the Kernel's audit decision."""

    verdict: VerdictType
    paseto_token: Optional[str] = None
    stochastic_drift_index: float
    principal_authority_id: str
    intent_id: str
    jurisdiction: str
    regime_context: Optional[str] = None
    axis_1_action_verdict: Axis1ActionVerdict
    axis_2_evaluation_evidence: Axis2EvaluationEvidence
    evaluated_checks: list[EvaluatedCheck]
    decision_reason: str


class ExecutionTrace(BaseModel):
    """Trace emitted by the Gate after enforcing an action execution."""

    intent_id: str
    final_state: Literal["EXECUTED", "BLOCKED", "REMEDIATED"]
    axis_1_action_verdict: Axis1ActionVerdict
    axis_2_evaluation_evidence: Axis2EvaluationEvidence
    executed_payload: dict[str, Any] = Field(default_factory=dict)
    enforcement_timestamp: str
    decision_reason: str


# Governance Mocks for Local Testing
MOCK_USER_DB: dict[str, dict[str, Any]] = {
    "usr_001": {
        "name": "Alice Corp Admin",
        "role": "TREASURY_OPERATOR",
        "clearance_level": 3,
        "active_delegations": ["agent-007"],
    }
}

# Registered Governance Policies
MOCK_POLICIES: dict[str, dict[str, Any]] = {
    "FINRA_US": {
        "auto_approve_limit": 500.0,
        "escalation_threshold": 2000.0,
        "disallowed_jurisdictions": ["CU", "IR", "KP", "SY"],
        "max_risk_score": 0.80,
    }
}