import pytest
from cda.kernel.engine import authorize
from cda.gate.engine import GateExecutor
from cda.shared.models import Intent, ContextSnapshot

def test_full_security_lifecycle():
    """Validates the end-to-end flow: Intent -> Kernel -> Gate."""
    # 1. Setup Trusted Context with sufficient balance
    context = ContextSnapshot(
        entity_id="user-456",
        state={"balance": 5000, "version": 10}
    )

    # 2. Setup Agent Intent
    intent = Intent(
        entity_id="user-456",
        source="autonomous-agent-01",
        action="execute_trade",
        params={"amount": 1000}
    )

    # 3. Kernel Authorization (Generates PASETO Token)
    auth_result = authorize(intent, context)
    assert auth_result["decision"] == "allow"
    token = auth_result["token"]

    # 4. Gate Verification
    gate = GateExecutor()
    manifest = gate.verify_token(token)
    assert manifest["action"] == "execute_trade"
    assert manifest["entity_id"] == "user-456"

def test_policy_violation_insufficient_balance():
    """Ensures rejection when balance is lower than requested amount."""
    context = ContextSnapshot(entity_id="user-456", state={"balance": 10})
    intent = Intent(
        entity_id="user-456", 
        source="agent", 
        action="execute_trade", 
        params={"amount": 1000}
    )

    with pytest.raises(ValueError, match="Insufficient balance"):
        authorize(intent, context)