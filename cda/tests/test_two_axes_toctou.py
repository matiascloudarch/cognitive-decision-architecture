# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

from typing import Any
from unittest.mock import patch

from cda.gate.engine import ExecutionRequest, execute_action
from cda.kernel.engine import authorize_intent
from cda.shared.models import AgentIntent

TEST_ENTITY_ID = "usr_001"


def test_two_axes_permit_and_execute() -> None:
    intent = AgentIntent(
        entity_id=TEST_ENTITY_ID,
        agent_id="agent-test",
        action="test",
        params={"amount": 50.0},
        regime_context="FINRA_US",
        jurisdiction="US",
    )
    decision = authorize_intent(intent)
    assert decision.verdict == "PERMIT"

    req = ExecutionRequest(
        target_service="test_svc",
        action="test",
        params={"amount": 50.0},
        global_context_freeze=False,
    )
    trace = execute_action(req, f"Bearer {decision.paseto_token}")
    assert trace.final_state == "EXECUTED"


def test_two_axes_remediate_and_enforce() -> None:
    intent = AgentIntent(
        entity_id=TEST_ENTITY_ID,
        agent_id="agent-test",
        action="test",
        params={"amount": 1500.0},
        regime_context="FINRA_US",
        jurisdiction="US",
    )
    decision = authorize_intent(intent)
    assert decision.verdict == "REMEDIATE"

    req = ExecutionRequest(
        target_service="test_svc",
        action="test",
        params={"amount": 1500.0},
        global_context_freeze=False,
    )
    trace = execute_action(req, f"Bearer {decision.paseto_token}")
    assert trace.final_state == "REMEDIATED"
    assert trace.executed_payload["amount"] == 500.0


@patch("pyseto.decode")
def test_two_axes_expired_lease(mock_decode: Any) -> None:
    from pyseto.exceptions import VerifyError
    mock_decode.side_effect = VerifyError("Expired")

    intent = AgentIntent(
        entity_id=TEST_ENTITY_ID,
        agent_id="agent-test",
        action="test",
        params={"amount": 50.0},
        regime_context="FINRA_US",
        jurisdiction="US",
    )
    decision = authorize_intent(intent)

    req = ExecutionRequest(
        target_service="test_svc",
        action="test",
        params={"amount": 50.0},
        global_context_freeze=False,
    )
    trace = execute_action(req, f"Bearer {decision.paseto_token}")
    assert trace.final_state == "BLOCKED"
    assert trace.axis_2_evaluation_evidence.execution_status == "INVALID_TOKEN"


def test_toctou_stale_context_freeze() -> None:
    intent = AgentIntent(
        entity_id=TEST_ENTITY_ID,
        agent_id="agent-test",
        action="test",
        params={"amount": 50.0},
        regime_context="FINRA_US",
        jurisdiction="US",
    )
    decision = authorize_intent(intent)

    req = ExecutionRequest(
        target_service="test_svc",
        action="test",
        params={"amount": 50.0},
        global_context_freeze=True,
    )
    trace = execute_action(req, f"Bearer {decision.paseto_token}")
    assert trace.final_state == "BLOCKED"
    assert trace.axis_2_evaluation_evidence.execution_status == "UNRESOLVED_DEPENDENCY_OR_STALE_CONTEXT"


def test_syntactic_payload_tamper_lock() -> None:
    intent = AgentIntent(
        entity_id=TEST_ENTITY_ID,
        agent_id="agent-test",
        action="test",
        params={"amount": 50.0},
        regime_context="FINRA_US",
        jurisdiction="US",
    )
    decision = authorize_intent(intent)

    req = ExecutionRequest(
        target_service="test_svc",
        action="test",
        params={"amount": 999.0},
        global_context_freeze=False,
    )
    trace = execute_action(req, f"Bearer {decision.paseto_token}")
    assert trace.final_state == "BLOCKED"
    assert trace.axis_2_evaluation_evidence.failure_mode == "PAYLOAD_TAMPERING_DETECTED"