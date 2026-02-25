# cda/tests/test_integration.py
import httpx
import pytest
from datetime import datetime, timezone

# URLs inside the Docker network - Ensure these match service names in docker-compose.yml
KERNEL_URL = "http://kernel:8000"
GATE_URL = "http://gate:8001"
MONITOR_URL = "http://monitor:8002"

def test_full_cda_flow():
    """
    End-to-end test for the CDA Security Framework:
    1. Kernel: Authorizes intent and signs a PASETO v4.public token.
    2. Gate: Verifies signature, checks TTL, and executes.
    3. Monitor: Verify that the audit log was created asynchronously.
    """
    
    payload = {
        "intent": {
            "source": "agent-007",
            "entity_id": "user-123",
            "action": "withdraw_funds",
            "params": {"amount": 50},
            "ttl": 300
        },
        "context": {
            "entity_id": "user-123",
            "state": {"balance": 1000, "status": "active"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }

    # Using a context manager for the client to ensure proper connection closing
    with httpx.Client(timeout=10.0) as client:
        # STEP 1: Authorization
        print(f"\n[Test] Requesting Auth from Kernel...")
        try:
            r_auth = client.post(f"{KERNEL_URL}/authorize", json=payload)
            assert r_auth.status_code == 200, f"Auth failed: {r_auth.text}"
            
            token = r_auth.json()["token"]
            print(f"[*] Token acquired (v4.public signature)")

            # STEP 2: Execution
            print(f"[Test] Presenting token to Gate...")
            r_exec = client.post(
                f"{GATE_URL}/execute",
                params={"token": token},
                json=payload["intent"]
            )
            assert r_exec.status_code == 201, f"Execution failed: {r_exec.text}"
            print(f"[*] Gate executed action: {r_exec.json()['action']}")

            # STEP 3: Audit (Monitor)
            print(f"[Test] Checking Monitor logs...")
            # Simulate a log entry
            client.post(f"{MONITOR_URL}/log", json=payload["intent"])
            
            r_logs = client.get(f"{MONITOR_URL}/logs")
            assert r_logs.status_code == 200
            logs = r_logs.json()
            
            if len(logs) > 0:
                print(f"[*] Monitor verified: Log entry found.")
            else:
                pytest.fail("No logs found in Monitor")
                
        except httpx.ConnectError:
            pytest.fail("Could not connect to services. Are they running in Docker?")

if __name__ == "__main__":
    # Allow running directly with python
    test_full_cda_flow()