import os
import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, status
from pyseto import Key, Paseto
from dotenv import load_dotenv

from cda.shared.models import Intent, MOCK_USER_DB, MOCK_POLICIES

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cda-kernel")

app = FastAPI(title="CDA Decision Kernel", version="16.0.0")

SECRET_KEY_RAW = os.getenv("CDA_SECRET_KEY", "internal_development_secret_key_fixed_32_chars")
KERNEL_KEY = Key.new(version=4, purpose="local", key=SECRET_KEY_RAW.encode())

def get_policy_version_hash():
    """Generates a hash of the current rules to ensure audit integrity."""
    policy_string = json.dumps(MOCK_POLICIES, sort_keys=True)
    return hashlib.sha256(policy_string.encode()).hexdigest()[:12]

@app.get("/")
async def health():
    return {"status": "online", "policy_version": get_policy_version_hash()}

@app.post("/authorize")
async def authorize(intent: Intent, human_signature: Optional[str] = None):
    user_data = MOCK_USER_DB.get(intent.entity_id)
    policy = MOCK_POLICIES.get(intent.action)
    
    if not user_data or not policy:
        raise HTTPException(status_code=400, detail="Entity or Policy not found")

    amount = intent.params.get("amount", 0)
    policy_hash = get_policy_version_hash()

    # Case: Escalation
    if amount > policy["require_human_above"] and not human_signature:
        return {
            "decision": "REQUIRES_HUMAN_REVIEW",
            "policy_violated": policy_hash,
            "rules": f"Limit {policy['require_human_above']} exceeded. Review required."
        }

    # Case: Authorized
    manifest = {
        "intent_id": str(intent.id),
        "agent_id": intent.agent_id,
        "action": intent.action,
        "amount": amount,
        "policy_version": policy_hash,
        "approval_type": "human_verified" if human_signature else "auto_approved",
        "human_auditor": human_signature,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    token = Paseto.new().encode(KERNEL_KEY, payload=json.dumps(manifest).encode(), footer=b"cda-v16")
    
    return {"decision": "ALLOW", "paseto_token": token.decode(), "audit_trail": manifest}