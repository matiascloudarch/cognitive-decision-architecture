import pytest
import json
from pyseto import Paseto, Key
from cda.kernel.engine import authorize, KERNEL_KEY
from cda.shared.models import Intent, ContextSnapshot

def test_full_security_lifecycle():
    """Validates the cryptographic handoff between Kernel logic and Gate verification."""
    
    # 1. Setup Trusted Context
    context = ContextSnapshot(
        entity_id="user-789",
        state={"balance": 1000, "version": 1}
    )

    # 2. Setup Agent Intent
    intent = Intent(
        entity_id="user-789",
        source="agent-007",
        action="transfer_funds",
        params={"amount": 500}
    )

    # 3. Kernel Decision (Produces Token)
    result = authorize(intent, context)
    assert result["decision"] == "allow"
    token = result["token"]

    # 4. Gate-side verification logic simulation
    decoded = Paseto.new().decode(KERNEL_KEY, token)
    manifest = json.loads(decoded.payload)
    
    assert manifest["action"] == "transfer_funds"
    assert manifest["entity_id"] == "user-789"
    assert manifest["intent_id"] == str(intent.id)

def test_insufficient_balance_rejection():
    """Checks that the Kernel enforces policies before signing tokens."""
    context = ContextSnapshot(entity_id="user-1", state={"balance": 5})
    intent = Intent(entity_id="user-1", source="agent", action="buy", params={"amount": 100})

    with pytest.raises(ValueError, match="Insufficient balance"):
        authorize(intent, context)