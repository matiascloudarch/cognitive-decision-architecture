# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

from fastapi.testclient import TestClient

from cda.kernel.engine import app

client = TestClient(app)


def test_unmapped_regime_context() -> None:
    intent_data = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 100.0},
        "regime_context": "UNKNOWN_REGIME",
        "jurisdiction": "US",
    }
    response = client.post("/authorize", json=intent_data)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "INDETERMINATE"
    assert data["paseto_token"] is None
    assert data["axis_2_evaluation_evidence"]["execution_status"] == "INVALID_REGIME_CONTEXT"
    assert data["axis_2_evaluation_evidence"]["failure_mode"] == "INVALID_REGIME_CONTEXT"


def test_valid_permit_request() -> None:
    intent_data = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 150.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post("/authorize", json=intent_data)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "PERMIT"
    assert data["paseto_token"] is not None
    assert data["axis_1_action_verdict"]["state"] == "PERMIT"
    assert data["axis_2_evaluation_evidence"]["execution_status"] == "COMPLETE"


def test_remediation_request() -> None:
    intent_data = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 1000.0},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post("/authorize", json=intent_data)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "REMEDIATE"
    assert data["paseto_token"] is not None
    assert data["axis_1_action_verdict"]["state"] == "REMEDIATE"
    assert data["axis_1_action_verdict"]["remediation_details"]["adjusted_payload"]["amount"] == 500.0