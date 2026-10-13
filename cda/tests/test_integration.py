# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

from fastapi.testclient import TestClient

from cda.gate.engine import app as gate_app
from cda.kernel.engine import app as kernel_app

kernel_client = TestClient(kernel_app)
gate_client = TestClient(gate_app)


def test_full_two_axis_flow() -> None:
    intent_data = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }

    # 1. Authorize via Kernel
    auth_res = kernel_client.post("/authorize", json=intent_data)
    assert auth_res.status_code == 200
    auth_json = auth_res.json()
    assert auth_json["verdict"] == "PERMIT"
    token = auth_json["paseto_token"]
    assert token is not None

    # 2. Execute via Gate
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
    exec_json = exec_res.json()
    assert exec_json["final_state"] == "EXECUTED"