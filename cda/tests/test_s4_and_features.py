# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

"""
Integration tests for Gate features and Operational limits (S4).
"""

from cda.gate.engine import GLOBAL_CIRCUIT_BREAKER, ExecutionRequest
from cda.kernel.engine import authorize_intent
from cda.shared.models import AgentIntent

TEST_ENTITY = "usr_001"
TEST_AGENT = "agent-s4-test"


def test_s4_refund_flow_permit() -> None:
    intent = AgentIntent(
        entity_id=TEST_ENTITY,
        agent_id=TEST_AGENT,
        action="refund",
        params={"amount": 50.0},
        regime_context="FINRA_US",
        jurisdiction="US",
    )
    decision = authorize_intent(intent)

    assert intent.params["amount"] == 50.0
    assert decision.verdict == "PERMIT"
    assert decision.paseto_token is not None


def test_s4_refund_flow_remediate() -> None:
    intent = AgentIntent(
        entity_id=TEST_ENTITY,
        agent_id=TEST_AGENT,
        action="refund",
        params={"amount": 1200.0},
        regime_context="FINRA_US",
        jurisdiction="US",
    )
    decision = authorize_intent(intent)

    assert intent.params["amount"] == 1200.0
    assert decision.verdict == "REMEDIATE"
    assert decision.paseto_token is not None
    assert decision.axis_1_action_verdict.state == "REMEDIATE"
    assert decision.axis_1_action_verdict.remediation_details is not None
    assert decision.axis_1_action_verdict.remediation_details.adjusted_payload["amount"] == 500.0


def test_gate_circuit_breaker() -> None:
    GLOBAL_CIRCUIT_BREAKER.reset("agent_test_cb")
    for _ in range(GLOBAL_CIRCUIT_BREAKER.max_requests + 1):
        GLOBAL_CIRCUIT_BREAKER.record_request("agent_test_cb")

    assert GLOBAL_CIRCUIT_BREAKER.is_tripped("agent_test_cb")

    ExecutionRequest(
        target_service="test",
        action="test",
        params={},
        global_context_freeze=False,
    )