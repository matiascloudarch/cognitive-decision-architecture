import os
import json
from datetime import datetime, timezone
from typing import Dict
from fastapi import FastAPI, HTTPException, status
from pyseto import Key, Paseto
from dotenv import load_dotenv
from cda.shared.models import Intent, ContextSnapshot

# Load environment variables from .env file
load_dotenv()

# --- SECURITY VALIDATION ---
# Load the private key for asymmetric signing (V4.Public)
# Source: CDA Architecture V13.4 Security Protocol
PRIVATE_KEY_RAW = os.getenv("PASETO_PRIVATE_KEY")
if not PRIVATE_KEY_RAW:
    raise RuntimeError("CRITICAL: PASETO_PRIVATE_KEY is not defined in environment.")

# Initialize the Kernel Key as a V4 Public Signing Key
KERNEL_KEY = Key.new(version=4, purpose="public", key=PRIVATE_KEY_RAW.encode())

app = FastAPI(title="CDA Decision Kernel - Production Ready")

def authorize(intent: Intent, context: ContextSnapshot) -> Dict:
    """
    Core Authorization Logic.
    Validates agent intent against trusted context and issues a signed PASETO v4 token.
    """
    # 1. Identity Verification
    if intent.entity_id != context.entity_id:
        raise ValueError("Security Violation: Entity ID mismatch between Intent and Context.") [cite: 251, 252]
    
    # 2. Policy Enforcement (Example: Balance Check)
    balance = context.state.get("balance", 0) [cite: 253]
    amount_requested = intent.params.get("amount", 0) [cite: 253]
    
    if balance < amount_requested:
        raise ValueError("Policy Violation: Insufficient funds for requested action.") [cite: 254, 255]

    # 3. Decision Manifest Creation
    manifest = {
        "intent_id": str(intent.id),
        "entity_id": intent.entity_id,
        "action": intent.action,
        "decision": "allow",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ttl": intent.ttl
    } [cite: 256, 262, 263]

    # 4. Asymmetric Signing (V4.Public)
    # This prevents the 'Schizophrenia' error by using digital signatures.
    token = Paseto.encode(
        KERNEL_KEY,
        payload=json.dumps(manifest).encode(),
        footer=b"cda-v13.4"
    ) [cite: 265, 267, 268]

    return {
        "decision": "allow",
        "token": token.decode() if isinstance(token, bytes) else token,
        "manifest_preview": manifest
    } [cite: 270, 273, 274]

@app.post("/authorize")
async def authorize_endpoint(intent: Intent, context: ContextSnapshot) -> Dict:
    """FastAPI endpoint for decision making."""
    try:
        return authorize(intent, context)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) [cite: 275, 280]