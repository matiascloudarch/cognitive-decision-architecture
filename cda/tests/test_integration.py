import httpx
import pytest

# Local URLs for testing (assuming services are running)
KERNEL_URL = "http://127.0.0.1:8000"
GATE_URL = "http://127.0.0.1:8001"

def test_full_governance_flow():
    """
    Integration test for the full CDA lifecycle:
    Auth Request -> Decision -> Execution -> Forensic Log
    """
    intent_data = {
        "entity_id": "user-001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 100}
    }

    with httpx.Client(timeout=10.0) as client:
        # 1. AUTHORIZE
        r_auth = client.post(f"{KERNEL_URL}/authorize", json=intent_data)
        assert r_auth.status_code == 200
        token = r_auth.json()["paseto_token"]

        # 2. EXECUTE
        r_exec = client.post(f"{GATE_URL}/execute", params={"token": token})
        assert r_exec.status_code == 201
        assert r_exec.json()["status"] == "executed"
        
        # 3. VERIFY AUDIT LOG
        r_logs = client.get(f"{GATE_URL}/audit/logs")
        logs = r_logs.json()["logs"]
        assert any(log["intent_id"] == r_auth.json()["audit_trail"]["intent_id"] for log in logs)

if __name__ == "__main__":
    test_full_governance_flow()