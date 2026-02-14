import os
import json
from datetime import datetime, timezone
from typing import Dict
from fastapi import FastAPI, HTTPException, status
from pyseto import Key, Paseto
from dotenv import load_dotenv
from cda.shared.models import Intent, ContextSnapshot

load_dotenv()

# Security: Load secret from environment.
SECRET_KEY_RAW = os.getenv("CDA_SECRET_KEY")
if not SECRET_KEY_RAW or len(SECRET_KEY_RAW) < 32:
    raise RuntimeError("CDA_SECRET_KEY must be at least 32 characters long")

KERNEL_KEY = Key.new(version=4, purpose="local", key=SECRET_KEY_RAW.encode())

app = FastAPI(title="CDA Decision Kernel API")

def authorize(intent: Intent, context: ContextSnapshot) -> Dict:
    """Core authorization logic. Validates intent against context."""
    if intent.entity_id != context.entity_id:
        raise ValueError("Security Violation: Entity ID mismatch")

    balance = context.state.get("balance", 0)
    amount_requested = intent.params.get("amount", 0)

    if balance < amount_requested:
        raise ValueError("Policy Violation: Insufficient balance")

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
        KERNEL_KEY,
        payload=json.dumps(manifest).encode(),
        footer=b"cda-v13.4"
    )

    return {
        "decision": "allow",
        "token": token.decode(),
        "manifest_preview": manifest
    }

@app.post("/authorize")
def authorize_endpoint(intent: Intent, context: ContextSnapshot) -> Dict:
    try:
        return authorize(intent, context)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))