# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

from fastapi.testclient import TestClient

from cda.gate.engine import app as gate_app
from cda.kernel.engine import app as kernel_app

kernel_client = TestClient(kernel_app)
gate_client = TestClient(gate_app)


def test_gate_missing_token() -> None:
    gate_payload = {
        "target_service": "payment_gateway",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "global_context_freeze": False,
    }
    response = gate_client.post("/execute", json=gate_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["final_state"] == "BLOCKED"
    assert data["axis_2_evaluation_evidence"]["execution_status"] == "INVALID_TOKEN"


def test_gate_executed_flow() -> None:
    intent_data = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    auth_res = kernel_client.post("/authorize", json=intent_data)
    assert auth_res.status_code == 200
    token = auth_res.json()["paseto_token"]

    gate_payload = {
        "target_service": "payment_gateway",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "global_context_freeze": False,
    }
    exec_res = gate_client.post(
        "/execute",
        json=gate_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["final_state"] == "EXECUTED"
    assert data["axis_1_action_verdict"]["state"] == "PERMIT"


def test_gate_toctou_context_freeze() -> None:
    intent_data = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    auth_res = kernel_client.post("/authorize", json=intent_data)
    token = auth_res.json()["paseto_token"]

    gate_payload = {
        "target_service": "payment_gateway",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "global_context_freeze": True,
    }
    exec_res = gate_client.post(
        "/execute",
        json=gate_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["final_state"] == "BLOCKED"
    assert data["axis_2_evaluation_evidence"]["execution_status"] == "UNRESOLVED_DEPENDENCY_OR_STALE_CONTEXT"