"""
Integration tests for the Cognitive Decision Architecture (CDA) full execution flow.
Uses FastAPI TestClient for in-memory integration testing.
"""

import os
import sys

# Ensure shared environment variables for test execution
os.environ["PASETO_SECRET_KEY"] = "YELLOW_SUBMARINE_BLACK_WIZARD_KEY_32BYTES"

# Ensure root CDA modules are accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from fastapi.testclient import TestClient

from cda.kernel.engine import app as kernel_app
from cda.gate.engine import app as gate_app

kernel_client = TestClient(kernel_app)
gate_client = TestClient(gate_app)


def test_full_governance_flow():
    """
    Integration test for the full CDA lifecycle:
    Auth Request -> Decision -> Execution -> Forensic Log
    """
    intent_data = {
        "entity_id": "usr_001",
        "agent_id": "agent-007",
        "action": "transfer_funds",
        "params": {"amount": 100},
        "regime_context": "FINRA_US",
        "jurisdiction": "US"
    }

    # 1. AUTHORIZE VIA KERNEL
    r_auth = kernel_client.post("/authorize", json=intent_data)
    assert r_auth.status_code == 200
    
    auth_response = r_auth.json()
    assert auth_response["verdict"] == "PERMIT"
    
    token = auth_response.get("paseto_token")
    assert token is not None, "PASETO token should be present for PERMIT verdict"

    # 2. EXECUTE VIA GATE
    headers = {"Authorization": f"Bearer {token}"}
    r_exec = gate_client.post("/execute", headers=headers, params={"token": token})
    
    assert r_exec.status_code == 200, f"Execution failed: {r_exec.text}"
    exec_response = r_exec.json()
    assert exec_response["status"] == "EXECUTED"