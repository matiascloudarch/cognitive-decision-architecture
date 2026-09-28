import requests
import json
import os

# URL of the authorization endpoint (Deterministic Policy Kernel / PEP)
AUTHORIZE_URL = os.getenv("KERNEL_URL", "http://127.0.0.1:8000/authorize")

def simulate_hallucination():
    """
    Simulates a scenario where an LLM agent attempts an out-of-policy action.
    Must result in a DENY or REQUIRES_HUMAN_REVIEW.
    """
    print(f"\n--- LLM Agent Hallucination Simulation ---")
    print(f"Attempting to request an excessive transfer ($5000) without HITL Attestation.\n")

    # Simulation of an excessive amount request without HITL Attestation
    intent_data = {
        "entity_id": "user-001",
        "agent_id": "hallucinating-llm-agent",
        "action": "transfer_funds",
        "params": {
            "amount": 5000  # Excessive amount to force DENY or REQUIRES_HUMAN_REVIEW
        }
    }

    try:
        response = requests.post(AUTHORIZE_URL, json=intent_data)
        print(f"Respuesta del Deterministic Policy Kernel (PEP) [{response.status_code}]:")
        response_json = response.json()
        print(json.dumps(response_json, indent=2))

        if response.status_code == 400 and "Maximum limit exceeded" in response_json.get("detail", ""):
            print("\n✅ The Deterministic Policy Kernel (PEP) correctly blocked the intent (Fail-Closed).")
            print("   The transfer exceeded the maximum policy limit.")
        elif response_json.get("decision") == "REQUIRES_HUMAN_REVIEW":
            print("\n⚠️ The Deterministic Policy Kernel (PEP) escalated the intent for HITL Attestation.")
            print("   The transfer required human review and no attestation was provided.")
        else:
            print("\n❌ Unexpected behavior from the Deterministic Policy Kernel (PEP).")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection error: Ensure the Deterministic Policy Kernel (PEP) is running at {AUTHORIZE_URL}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    simulate_hallucination()
