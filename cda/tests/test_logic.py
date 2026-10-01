import pytest
from fastapi.testclient import TestClient
from cda.kernel.engine import app

client = TestClient(app)


def test_permit_verdict():
    payload = {
        "entity_id": "usr_001",
        "agent_id": "test-agent",
        "action": "transfer_funds",
        "params": {"amount": 100},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post("/authorize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "PERMIT"
    assert data["paseto_token"] is not None


def test_remediate_verdict():
    # Amount 750 is above auto_approve_limit (500) and below escalate_limit (1000)
    payload = {
        "entity_id": "usr_001",
        "agent_id": "test-agent",
        "action": "transfer_funds",
        "params": {"amount": 750},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post("/authorize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "REMEDIATE"
    assert data["paseto_token"] is not None


def test_escalate_verdict():
    payload = {
        "entity_id": "usr_001",
        "agent_id": "test-agent",
        "action": "transfer_funds",
        "params": {"amount": 1500},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post("/authorize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "ESCALATE"


def test_escalate_with_human_signature():
    payload = {
        "entity_id": "usr_001",
        "agent_id": "test-agent",
        "action": "transfer_funds",
        "params": {"amount": 1500},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post(
        "/authorize?human_signature=Matias-S", json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "PERMIT"


def test_block_verdict():
    payload = {
        "entity_id": "usr_001",
        "agent_id": "test-agent",
        "action": "transfer_funds",
        "params": {"amount": 15000},
        "regime_context": "FINRA_US",
        "jurisdiction": "US",
    }
    response = client.post("/authorize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "BLOCK"
    assert data.get("paseto_token") is None