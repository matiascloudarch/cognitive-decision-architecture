import json
from typing import Dict, Any

from fastapi import HTTPException
from pyseto import Key, Paseto

from cda.shared.models import Intent, ContextSnapshot


# ------------------------------------------------------------------
# Key material (DEVELOPMENT / DEMO ONLY)
#
# These keys are intentionally embedded for reference purposes.
# They MUST NOT be used in production.
# In real deployments, keys are loaded from a secure KMS or HSM.
# ------------------------------------------------------------------

_DEV_PRIVATE_KEY_PEM = b"""-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIMbiv7oa/TNtdDa0plGZ/msTc0oiKcx1feB3mhe5JP8Q
-----END PRIVATE KEY-----"""

_PRIVATE_KEY = Key.new(
    version=4,
    purpose="public",
    key=_DEV_PRIVATE_KEY_PEM,
)


# ------------------------------------------------------------------
# Policy evaluation (mirrors policy.rego)
# ------------------------------------------------------------------

def _evaluate_policy(intent: Intent, context: ContextSnapshot) -> None:
    """
    Enforces authorization rules.
    Raises HTTPException on denial.
    """

    if intent.action != "execute_trade":
        raise HTTPException(status_code=403, detail="Action not allowed")

    amount = intent.params.get("amount")
    if not isinstance(amount, (int, float)):
        raise HTTPException(status_code=403, detail="Invalid amount")

    balance = context.state.get("balance")
    if balance is None:
        raise HTTPException(status_code=403, detail="Balance not available")

    if amount > balance:
        raise HTTPException(status_code=403, detail="Insufficient balance")


# ------------------------------------------------------------------
# Kernel entrypoint
# ------------------------------------------------------------------

def authorize(intent: Intent, context: ContextSnapshot) -> Dict[str, Any]:
    """
    Authorizes an intent against a trusted context snapshot.
    Returns a signed authority token.
    """

    if intent.entity_id != context.entity_id:
        raise HTTPException(
            status_code=403,
            detail="Entity mismatch between intent and context",
        )

    _evaluate_policy(intent, context)

    manifest = {
        "intent_id": str(intent.id),
        "entity_id": intent.entity_id,
        "action": intent.action,
        "params": intent.params,
        "created_at": intent.created_at.isoformat(),
        "ttl": intent.ttl,
        "decision": "allow",
        "context_id": str(context.id),
        "entity_version": context.state.get("version"),
    }

    token = Paseto.new(exp=manifest["ttl"]).encode(
        _PRIVATE_KEY,
        json.dumps(manifest).encode(),
        b"cda-v13.3",
    )

    return {
        "token": token.decode(),
        "decision": "allow",
    }
