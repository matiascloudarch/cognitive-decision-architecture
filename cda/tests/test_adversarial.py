# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

from fastapi.testclient import TestClient

from cda.gate.engine import app as gate_app
from cda.kernel.engine import app as kernel_app

kernel_client = TestClient(kernel_app)
gate_client = TestClient(gate_app)


def test_adversarial_tampered_payload_blocked() -> None:
    """Verifies that tampering with the payload between Kernel authorization and Gate execution triggers a block."""
    intent_data = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US"
    }

    auth_res = kernel_client.post("/authorize", json=intent_data)
    assert auth_res.status_code == 200
    token = auth_res.json()["paseto_token"]
    assert token is not None

    # Adversarial tampering: Client sends amount = 9999.0 to Gate while token contains 100.0
    tampered_gate_payload = {
        "target_service": "payment_gateway",
        "action": "transfer_funds",
        "params": {"amount": 9999.0}
    }

    exec_res = gate_client.post(
        "/execute",
        json=tampered_gate_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["final_state"] == "BLOCKED"
    assert "Syntactic Payload Lock violation" in data["decision_reason"]


def test_adversarial_toctou_context_freeze_blocked() -> None:
    """Verifies that a context freeze / TOCTOU drift signal detected at execution time halts execution."""
    intent_data = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US"
    }

    auth_res = kernel_client.post("/authorize", json=intent_data)

    assert auth_res.status_code == 200
    token = auth_res.json()["paseto_token"]

    gate_payload = {
        "target_service": "payment_gateway",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "global_context_freeze": True
    }

    exec_res = gate_client.post(
        "/execute",
        json=gate_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["final_state"] == "BLOCKED"
    assert "TOCTOU drift" in data["decision_reason"]