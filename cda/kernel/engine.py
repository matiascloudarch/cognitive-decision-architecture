import json
from typing import Dict, Any
from fastapi import HTTPException
from pyseto import Key, Paseto
from cda.shared.models import Intent, ContextSnapshot

# DEVELOPMENT KEYS - DO NOT USE IN PRODUCTION
# In production, load from a secure KMS/HSM environment variable.
_DEV_PRIVATE_KEY_PEM = b"""-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIMbiv7oa/TNtdDa0plGZ/msTc0oiKcx1feB3mhe5JP8Q
-----END PRIVATE KEY-----"""

# PASETO v4.public uses asymmetric cryptography (Ed25519).
# Purpose "public" refers to the protocol version, using the private key to sign.
_SIGNING_KEY = Key.new(
    version=4,
    purpose="public", 
    key=_DEV_PRIVATE_KEY_PEM,
)

def authorize(intent: Intent, context: ContextSnapshot) -> Dict[str, Any]:
    """
    Stateless Authority: Evaluates intent against trusted context and signs the decision.
    """
    if intent.entity_id != context.entity_id:
        raise HTTPException(status_code=403, detail="Security Breach: Entity mismatch")

    # Policy enforcement (In production, call OPA/Rego engine here)
    if intent.params.get("amount", 0) > context.state.get("balance", 0):
        raise HTTPException(status_code=403, detail="Policy Violation: Insufficient balance")

    manifest = {
        "intent_id": str(intent.id),
        "entity_id": intent.entity_id,
        "action": intent.action,
        "params": intent.params,
        "created_at": intent.created_at.isoformat(),
        "ttl": intent.ttl,
        "decision": "allow",
        "entity_version": context.state.get("version"), # OCC lock
    }

    # Generate the Authority Token
    token = Paseto.new(exp=manifest["ttl"]).encode(
        _SIGNING_KEY,
        json.dumps(manifest).encode(),
        footer=b"cda-v13.3",
    )

    return {
        "token": token.decode(),
        "decision": "allow",
        "manifest_summary": manifest
    }