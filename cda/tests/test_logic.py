import pytest
from cda.kernel.engine import authorize
from cda.gate.engine import GateExecutor
from cda.shared.models import Intent, ContextSnapshot

def test_full_security_lifecycle():
    """
    Validates the end-to-end flow: Intent -> Kernel -> Gate.
    """
    # 1. Setup Trusted Context
    context = ContextSnapshot(
        entity_id="user-456",
        state={"balance": 5000, "version": 10}
    )

    # 2. Setup Agent Intent
    intent = Intent(
        entity_id="user-456",
        source="autonomous-agent-01",
        action="execute_trade",
        params={"amount": 1000},
        ttl=300
    )

    # 3. Kernel Authorization
    auth_result = authorize(intent, context)
    assert auth_result["decision"] == "allow"
    token = auth_result["token"]

    # 4. Gate Execution
    gate = GateExecutor()
    # Inject state into the mock Gate to match the Context Provider
    gate._state["user-456"] = {"version": 10, "balance": 5000}
    
    manifest = gate.verify_token(token)
    assert manifest["action"] == "execute_trade"
    assert manifest["entity_version"] == 10

    # This call should now succeed
    gate.execute(manifest)

def test_policy_violation_rejection():
    """
    Ensures the Kernel denies authorization if policy rules are breached.
    """
    context = ContextSnapshot(entity_id="user-456", state={"balance": 10, "version": 1})
    intent = Intent(
        entity_id="user-456", 
        source="agent", 
        action="execute_trade", 
        params={"amount": 1000}, # Violation
        ttl=60
    )

    with pytest.raises(Exception):
        authorize(intent, context)

def test_occ_concurrency_protection():
    """
    Ensures the Gate prevents execution if the state changed after signing.
    """
    context = ContextSnapshot(entity_id="user-456", state={"version": 5, "balance": 100})
    intent = Intent(entity_id="user-456", source="agent", action="execute_trade", ttl=60)

    token = authorize(intent, context)["token"]

    gate = GateExecutor()
    # Simulate an external update to the entity version
    gate._state["user-456"] = {"version": 6, "balance": 100}

    manifest = gate.verify_token(token)
    with pytest.raises(ValueError, match="Conflict: State evolved"):
        gate.execute(manifest)

def test_entity_mismatch_protection():
    """
    Ensures the Kernel blocks context hijacking between different entities.
    """
    context = ContextSnapshot(entity_id="victim-id", state={"version": 1, "balance": 0})
    intent = Intent(entity_id="attacker-id", source="agent", action="execute_trade", ttl=60)

    with pytest.raises(Exception):
        authorize(intent, context)