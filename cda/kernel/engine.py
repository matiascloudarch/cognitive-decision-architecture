import os
import json
from datetime import datetime, timezone
from typing import Dict
from fastapi import FastAPI, HTTPException, status
from pyseto import Key, Paseto
from dotenv import load_dotenv

from cda.shared.models import Intent, ContextSnapshot

load_dotenv()

# Security: Load secret from environment. Never hardcode in production.
SECRET_KEY_RAW = os.getenv("CDA_SECRET_KEY", "default-insecure-key-32-chars-!!")
KERNEL_KEY = Key.new(version=4, purpose="local", key=SECRET_KEY_RAW.encode())

app = FastAPI(title="CDA Decision Kernel API")

def authorize(intent: Intent, context: ContextSnapshot) -> Dict:
    """
    Core authorization logic. Validates intent against a trusted context snapshot.
    """
    # 1. Identity Validation
    if intent.entity_id != context.entity_id:
        raise ValueError("Security Violation: Entity ID mismatch")

    # 2. Business Logic (Example: Balance Check)
    balance = context.state.get("balance", 0)
    amount_requested = intent.params.get("amount", 0)

    if balance < amount_requested:
        raise ValueError("Policy Violation: Insufficient balance")

    # 3. Manifest Construction
    manifest = {
        "intent_id": str(intent.id),
        "entity_id": intent.entity_id,
        "entity_version": context.state.get("version", 0),
        "action": intent.action,
        "decision": "allow",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ttl": intent.ttl
    }

    # 4. PASETO Token Generation (V4 Local)
    token = Paseto.new().encode(
        KERNEL_KEY,
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
    """HTTP entry point for the Decision Kernel."""
    try:
        return authorize(intent, context)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Kernel Error")