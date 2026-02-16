import os
import requests
import pytest
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

# --- CONFIGURATION ---
# Use 'kernel' and 'gate' for Docker environment, or 'localhost' for local dev
KERNEL_URL = os.getenv("KERNEL_URL", "http://localhost:8000")
GATE_URL = os.getenv("GATE_URL", "http://localhost:8001")

def test_full_decision_execution_flow():
    """
    End-to-End Integration Test:
    1. Request authorization from Kernel.
    2. Verify the Asymmetric PASETO token.
    3. Execute the action via Gate.
    """
    entity_id = "agent_001"
    
    # Step 1: Define Intent and Context
    intent = {
        "id": str(uuid4()),
        "entity_id": entity_id,
        "action": "withdraw",
        "params": {"amount": 50},
        "ttl": 3600
    }
    
    context = {
        "entity_id": entity_id,
        "state": {"balance": 1000},
        "timestamp": "2024-02-16T12:00:00Z"
    }

    # Step 2: Get Authorization from Kernel
    auth_response = requests.post(f"{KERNEL_URL}/authorize", json={"intent": intent, "context": context})
    assert auth_response.status_code == 200
    
    data = auth_response.json()
    assert data["decision"] == "allow"
    token = data["token"]

    # Step 3: Execute via Gate
    exec_response = requests.post(f"{GATE_URL}/execute", params={"token": token})
    assert exec_response.status_code == 201
    assert exec_response.json()["status"] == "executed"

def test_replay_attack_prevention():
    """
    Security Test: Ensure the same token cannot be used twice.
    """
    entity_id = "agent_002"
    intent = {
        "id": str(uuid4()),
        "entity_id": entity_id,
        "action": "payment",
        "params": {"amount": 10},
        "ttl": 300
    }
    context = {"entity_id": entity_id, "state": {"balance": 100}, "timestamp": "2024-02-16T12:00:00Z"}

    # Get token
    auth_data = requests.post(f"{KERNEL_URL}/authorize", json={"intent": intent, "context": context}).json()
    token = auth_data["token"]

    # First execution: Success
    first_attempt = requests.post(f"{GATE_URL}/execute", params={"token": token})
    assert first_attempt.status_code == 201

    # Second execution (Replay): Must fail with 409 Conflict
    second_attempt = requests.post(f"{GATE_URL}/execute", params={"token": token})
    assert second_attempt.status_code == 409
    assert "Replay Attack Detected" in second_attempt.json()["detail"]

if __name__ == "__main__":
    # Manual execution helper
    pytest.main([__file__])