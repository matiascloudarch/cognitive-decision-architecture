# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

"""
Tests for the immutable, append-only Audit Ledger cryptographically signing all Axis 1/2 decisions.
"""

from typing import Any

from cda.ledger.audit import GLOBAL_AUDIT_LEDGER, AuditLedger
from cda.shared.models import AuditDecision


def get_mock_decision(verdict: str) -> AuditDecision:
    return AuditDecision(
        verdict=verdict,  # type: ignore[arg-type]
        paseto_token=None,
        stochastic_drift_index=0.1,
        principal_authority_id="usr_001",
        intent_id="int_123",
        jurisdiction="US",
        regime_context="FINRA_US",
        axis_1_action_verdict={  # type: ignore[arg-type]
            "state": verdict,
            "fallback_action": None,
            "remediation_details": None,
        },
        axis_2_evaluation_evidence={  # type: ignore[arg-type]
            "execution_status": "COMPLETE",
            "checks_executed": ["CHK-01"],
            "failure_mode": None,
        },
        evaluated_checks=[],
        decision_reason="Mock decision for ledger test",
    )


def test_append_record() -> None:
    ledger = AuditLedger()
    decision = get_mock_decision("PERMIT")
    params: dict[str, Any] = {"amount": 100.0}

    envelope = ledger.record_decision(decision, "agent-007", params)

    assert envelope.envelope_id == "env_000001"
    assert envelope.sequence_id == 1
    assert envelope.intent_id == "int_123"
    assert envelope.prev_hash == ledger.genesis_hash


def test_chain_integrity() -> None:
    ledger = AuditLedger()
    decision1 = get_mock_decision("PERMIT")
    decision2 = get_mock_decision("BLOCK")

    ledger.record_decision(decision1, "agent-007", {"amount": 100})
    ledger.record_decision(decision2, "agent-007", {"amount": 9999})

    assert ledger.verify_integrity() is True


def test_tamper_detection() -> None:
    ledger = AuditLedger()
    decision = get_mock_decision("PERMIT")
    ledger.record_decision(decision, "agent-007", {"amount": 100})

    # Tamper with the internal state
    ledger.ledger[0].verdict = "BLOCK"

    assert ledger.verify_integrity() is False


def test_global_audit_ledger() -> None:
    assert isinstance(GLOBAL_AUDIT_LEDGER, AuditLedger)