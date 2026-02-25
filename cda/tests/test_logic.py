import pytest
from cda.kernel.engine import KERNEL_KEY
from cda.shared.models import Intent, MOCK_USER_DB

# We test the logic via the app's internal functions or simulated requests
from fastapi.testclient import TestClient
from cda.kernel.engine import app

client = TestClient(app)

def test_auto_approval_logic():
    """Tests that amounts under the limit are approved automatically."""
    payload = {
        "entity_id": "user-001",
        "agent_id": "test-agent",
        "action": "transfer_funds",
        "params": {"amount": 100}
    }
    response = client.post("/authorize", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "ALLOW"
    assert "paseto_token" in response.json()

def test_human_escalation_logic():
    """Tests that high amounts trigger a REQUIRES_HUMAN_REVIEW status."""
    payload = {
        "entity_id": "user-001",
        "agent_id": "test-agent",
        "action": "transfer_funds",
        "params": {"amount": 900}
    }
    response = client.post("/authorize", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "REQUIRES_HUMAN_REVIEW"

def test_human_signature_approval():
    """Tests that providing a human signature unlocks the authorization."""
    payload = {
        "entity_id": "user-001",
        "agent_id": "test-agent",
        "action": "transfer_funds",
        "params": {"amount": 900}
    }
    # Resubmitting with human signature
    response = client.post("/authorize?human_signature=Matias-S", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "ALLOW"
    assert response.json()["audit_trail"]["human_auditor"] == "Matias-S"