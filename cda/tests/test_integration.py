import httpx
from datetime import datetime, timezone

KERNEL_URL = "http://127.0.0.1:8000"
GATE_URL = "http://127.0.0.1:8001"

def test_full_flow():
    # Final adjustments based on Pydantic's strict requirements:
    full_payload = {
        "intent": {
            "source": "agent-001",
            "entity_id": "agent-001",  # Field was missing in the last run
            "action": "deploy_resource",
            "params": {"region": "us-east-1"}
        },
        "context": {
            "entity_id": "agent-001",
            "source_ip": "127.0.0.1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            # 'state' must be a dictionary, not a string
            "state": {"status": "active", "health": "good"} 
        }
    }
    
    with httpx.Client() as client:
        # 1. Authorize with the Kernel
        print(f"\n[Test] Sending payload with dictionary state to Kernel...")
        r_auth = client.post(f"{KERNEL_URL}/authorize", json=full_payload)
        
        if r_auth.status_code == 422:
            print(f"❌ Kernel Validation Error (422): {r_auth.json()}")
            return
        elif r_auth.status_code != 200:
            print(f"❌ Kernel Error ({r_auth.status_code}): {r_auth.text}")
            return

        data = r_auth.json()
        token = data["token"]
        print(f"✅ Token received: {token[:30]}...")

        # 2. Execute via the Gate
        print(f"[Test] Presenting token to Gate...")
        r_exec = client.post(f"{GATE_URL}/execute", params={"token": token})
        
        if r_exec.status_code != 201:
            print(f"❌ Gate Execution Error ({r_exec.status_code}): {r_exec.json()}")
            return
            
        print("✅ Gate execution successful!")

if __name__ == "__main__":
    test_full_flow()