import os
import json
import sqlite3
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import pyseto
from pyseto import Key
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Cognitive Decision Architecture - Enforcement Gate",
    version="1.0.0",
)

DB_PATH = "cda_gate.db"

# Ensure a fixed 32-byte secret key matching Kernel definition perfectly
SECRET_HEX = os.getenv(
    "CDA_SECRET_HEX", 
    "707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f"
)
PASSERBY_SECRET_KEY = bytes.fromhex(SECRET_HEX)


def get_db_connection() -> sqlite3.Connection:
    """
    Creates a database connection with busy timeout and WAL mode enabled
    to prevent database locking during concurrent operations.
    """
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_db() -> None:
    """Initialize SQLite database for forensic audit logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS forensic_audit_trail (
            intent_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            action TEXT NOT NULL,
            amount REAL,
            verdict TEXT NOT NULL,
            principal_authority_id TEXT NOT NULL,
            regime_context TEXT NOT NULL,
            jurisdiction TEXT NOT NULL,
            approval_type TEXT NOT NULL,
            human_auditor TEXT,
            policy_version TEXT NOT NULL,
            execution_graph_hash TEXT NOT NULL,
            executed_at TEXT NOT NULL,
            receipt_hash TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


class AuditLogResponse(BaseModel):
    total_records: int
    logs: List[Dict[str, Any]]


@app.post("/execute")
def execute_action(token: str) -> Dict[str, Any]:
    """Verify PASETO v4 token and execute the authorized decision."""
    try:
        key = Key.new(version=4, purpose="local", key=PASSERBY_SECRET_KEY)
        decoded_paseto = pyseto.decode(key, token)
        
        payload_raw = decoded_paseto.payload
        if isinstance(payload_raw, bytes):
            payload = json.loads(payload_raw.decode("utf-8"))
        elif isinstance(payload_raw, dict):
            payload = payload_raw
        else:
            payload = json.loads(str(payload_raw))

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid, expired, or tampered PASETO token: {str(exc)}",
        )

    intent_id = payload.get("intent_id")
    agent_id = payload.get("agent_id")
    action = payload.get("action")
    params = payload.get("params", {})
    amount = params.get("amount", 0.0)
    verdict = payload.get("verdict")
    principal_authority_id = payload.get("principal_authority_id")
    regime_context = payload.get("regime_context")
    jurisdiction = payload.get("jurisdiction")
    approval_type = payload.get("approval_type")
    human_auditor = payload.get("human_auditor")
    policy_version = payload.get("policy_version")
    execution_graph_hash = payload.get("execution_graph_hash")
    issued_at = payload.get("issued_at")
    receipt_hash = payload.get("receipt_hash")

    if verdict not in ["PERMIT", "REMEDIATE"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Execution blocked for verdict: {verdict}",
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO forensic_audit_trail (
                intent_id, agent_id, action, amount, verdict,
                principal_authority_id, regime_context, jurisdiction,
                approval_type, human_auditor, policy_version,
                execution_graph_hash, executed_at, receipt_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                intent_id,
                agent_id,
                action,
                amount,
                verdict,
                principal_authority_id,
                regime_context,
                jurisdiction,
                approval_type,
                human_auditor,
                policy_version,
                execution_graph_hash,
                issued_at,
                receipt_hash,
            ),
        )
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Database constraint error: {str(e)}. Ensure payload has all required fields.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database execution error: {str(exc)}",
        )

    return {
        "status": "EXECUTED",
        "verdict": verdict,
        "forensic_receipt_hash": receipt_hash,
        "execution_graph_hash": execution_graph_hash,
    }


@app.get("/audit/logs", response_model=AuditLogResponse)
def get_audit_logs(limit: int = 50) -> AuditLogResponse:
    """Retrieve immutable forensic audit logs from the storage engine."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT intent_id, agent_id, action, amount, verdict,
               principal_authority_id, regime_context, jurisdiction,
               approval_type, human_auditor, policy_version,
               execution_graph_hash, executed_at, receipt_hash
        FROM forensic_audit_trail
        ORDER BY executed_at DESC
        LIMIT ?
    """,
        (limit,),
    )

    rows = cursor.fetchall()
    conn.close()

    logs = [dict(row) for row in rows]
    return AuditLogResponse(total_records=len(logs), logs=logs)