import json
from datetime import datetime, timezone
from typing import Dict
from fastapi import FastAPI, HTTPException
from pyseto import Key, Paseto

from cda.shared.models import Intent, ContextSnapshot

app = FastAPI(title="CDA Decision Kernel API")

# Use a static 32-byte key for development consistency
_DEV_KEY = Key.new(version=4, purpose="local", key=b"a-very-secret-key-32-chars-long-!!")

def authorize(intent: Intent, context: ContextSnapshot) -> Dict:
    """
    Core authorization logic used by both the API and internal tests.
    """
    if intent.entity_id != context.entity_id:
        raise ValueError("Security Violation: Entity mismatch")

    balance = context.state.get("balance", 0)
    amount_requested = intent.params.get("amount", 0)

    if balance < amount_requested:
        raise ValueError("Insufficient balance")

    manifest = {
        "intent_id": str(intent.id),
        "entity_id": intent.entity_id,
        "entity_version": context.state.get("version", 0),
        "action": intent.action,
        "decision": "allow",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ttl": intent.ttl
    }

    token = Paseto.new().encode(
        _DEV_KEY,
        payload=json.dumps(manifest).encode(),
        footer=b"cda-v13.3"
    )

    return {
        "decision": "allow",
        "token": token.decode(),
        "manifest_preview": manifest
    }

@app.get("/health")
def health_check():
    return {"status": "operational", "service": "kernel"}

@app.post("/authorize")
def authorize_endpoint(intent: Intent, context: ContextSnapshot) -> Dict:
    """
    HTTP Wrapper for the authorize logic.
    """
    try:
        return authorize(intent, context)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))