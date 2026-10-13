# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

from fastapi.testclient import TestClient

from cda.kernel.engine import app

client = TestClient(app)


def test_permit_within_limits() -> None:
    intent = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 250.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post("/authorize", json=intent)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "PERMIT"
    assert data["paseto_token"] is not None


def test_remediate_over_auto_limit() -> None:
    intent = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 1500.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post("/authorize", json=intent)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "REMEDIATE"
    assert data["axis_1_action_verdict"]["state"] == "REMEDIATE"
    assert data["axis_1_action_verdict"]["remediation_details"]["adjusted_payload"]["amount"] == 500.0


def test_escalate_over_escalation_limit() -> None:
    intent = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 5000.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post("/authorize", json=intent)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "ESCALATE"
    assert data["paseto_token"] is None
    assert data["axis_1_action_verdict"]["state"] == "ESCALATE"


def test_human_override_permit() -> None:
    intent = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 5000.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post("/authorize?human_signature=OVERRIDE_001", json=intent)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "PERMIT"
    assert data["paseto_token"] is not None


def test_sanctioned_jurisdiction_block() -> None:
    intent = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "SY",
    }
    response = client.post("/authorize", json=intent)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "BLOCK"
    assert data["paseto_token"] is None