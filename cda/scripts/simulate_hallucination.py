import os
import json
import requests

AUTHORIZE_URL = os.getenv("KERNEL_URL", "http://127.0.0.1:8000/authorize")


def run_simulation(title: str, payload: dict, human_signature: str = None):
    print(f"\n--- Scenario: {title} ---")
    url = AUTHORIZE_URL
    if human_signature:
        url += f"?human_signature={human_signature}"

    try:
        response = requests.post(url, json=payload)
        print(f"Kernel Response Status [{response.status_code}]:")
        res_json = response.json()
        print(json.dumps(res_json, indent=2))
        return res_json
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Ensure CDA Kernel is running at {AUTHORIZE_URL}")
        return None


def main():
    print("==========================================================")
    print("CDA Kernel & Attested Evaluation Path Simulation Engine")
    print("==========================================================")

    # 1. PERMIT Scenario
    run_simulation(
        "1. Standard Within-Policy Intent (Auto-Approved PERMIT)",
        {
            "entity_id": "user-001",
            "agent_id": "llm-agent-01",
            "action": "transfer_funds",
            "params": {"amount": 250},
            "regime_context": "FINRA_US",
            "jurisdiction": "US"
        }
    )

    # 2. REMEDIATE Scenario
    run_simulation(
        "2. Mild Out-of-Policy Intent (Auto-Capped REMEDIATE)",
        {
            "entity_id": "user-001",
            "agent_id": "llm-agent-02",
            "action": "transfer_funds",
            "params": {"amount": 750},
            "regime_context": "EU_AI_ACT_HIGH_RISK",
            "jurisdiction": "DE"
        }
    )

    # 3. ESCALATE Scenario
    run_simulation(
        "3. High-Risk Intent without Signature (HITL ESCALATE)",
        {
            "entity_id": "user-001",
            "agent_id": "llm-agent-03",
            "action": "transfer_funds",
            "params": {"amount": 1500},
            "regime_context": "ISO_42001",
            "jurisdiction": "NG"
        }
    )

    # 4. ESCALATE + Human Signature Scenario
    run_simulation(
        "4. High-Risk Intent WITH Human Attestation (Approved PERMIT)",
        {
            "entity_id": "user-001",
            "agent_id": "llm-agent-03",
            "action": "transfer_funds",
            "params": {"amount": 1500},
            "regime_context": "ISO_42001",
            "jurisdiction": "NG"
        },
        human_signature="Matias-S"
    )

    # 5. BLOCK Scenario
    run_simulation(
        "5. Critical Boundary Violation (Fail-Closed BLOCK)",
        {
            "entity_id": "user-001",
            "agent_id": "hallucinating-llm-agent",
            "action": "transfer_funds",
            "params": {"amount": 99999},
            "regime_context": "ICAO_ANNEX_9",
            "jurisdiction": "AR"
        }
    )


if __name__ == "__main__":
    main()