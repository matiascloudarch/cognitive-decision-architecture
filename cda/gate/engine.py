import os
import json
import sqlite3
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, status, Query
from pyseto import Key, Paseto
from dotenv import load_dotenv
from cda.shared.models import MOCK_POLICIES


load_dotenv()
logger = logging.getLogger("cda-gate")
app = FastAPI(title="CDA Execution Gate", version="16.0.0")


def get_policy_version_hash() -> str:
    """Generates a hash of the current rules to ensure audit integrity."""
    policy_string = json.dumps(MOCK_POLICIES, sort_keys=True)
    return hashlib.sha256(policy_string.encode()).hexdigest()[:12]


SECRET_KEY_RAW = os.getenv("CDA_SECRET_KEY", "internal_development_secret_key_fixed_32_chars")
GATE_KEY = Key.new(version=4, purpose="local", key=SECRET_KEY_RAW.encode())
DB_PATH = "cda_gate.db"


def init_db() -> None:
    """Initializes the SQLite database for storing the forensic audit trail."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forensic_audit_trail (
            intent_id TEXT PRIMARY KEY,
            agent_id TEXT,
            action TEXT,
            amount REAL,
            approval_type TEXT,
            human_auditor TEXT,
            policy_version TEXT,
            executed_at TIMESTAMP,
            receipt_hash TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


@app.post("/execute", status_code=status.HTTP_201_CREATED)
async def execute(token: str = Query(...)) -> Dict[str, Any]:
    """Validates the PASETO attestation token and logs execution into the forensic ledger."""
    try:
        decoded = Paseto.new().decode(GATE_KEY, token)

        # Enhanced token footer validation
        if not decoded.footer.decode().startswith("cda-v16"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token footer"
            )

        payload = json.loads(decoded.payload)

        # Validate policy version
        if payload.get("policy_version") != get_policy_version_hash():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Policy version mismatch"
            )

        # Validate human signature if required
        if payload.get("approval_type") == "human_verified" and not payload.get("human_auditor"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing human auditor signature"
            )

        execution_time = datetime.now(timezone.utc).isoformat()
        receipt_hash = hashlib.sha256(f"{payload['intent_id']}-{execution_time}".encode()).hexdigest()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO forensic_audit_trail VALUES (?,?,?,?,?,?,?,?,?)",
            (
                payload["intent_id"],
                payload["agent_id"],
                payload["action"],
                payload["amount"],
                payload["approval_type"],
                payload["human_auditor"],
                payload["policy_version"],
                execution_time,
                receipt_hash,
            ),
        )
        conn.commit()
        conn.close()

        return {"status": "executed", "forensic_hash": receipt_hash}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/audit/logs")
async def get_audit_logs() -> Dict[str, Any]:
    """Exposes the forensic audit trail for inspection and verification."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM forensic_audit_trail ORDER BY executed_at DESC")
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"total_records": len(logs), "logs": logs}