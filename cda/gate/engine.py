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

load_dotenv()
logger = logging.getLogger("cda-gate")
app = FastAPI(title="CDA Execution Gate", version="16.0.0")

SECRET_KEY_RAW = os.getenv("CDA_SECRET_KEY", "internal_development_secret_key_fixed_32_chars")
GATE_KEY = Key.new(version=4, purpose="local", key=SECRET_KEY_RAW.encode())
DB_PATH = "cda_gate.db"

# (init_db remains the same, but adding policy_version to the table)
def init_db():
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

@app.post("/execute", status_code=201)
async def execute(token: str = Query(...)):
    try:
        decoded = Paseto.new().decode(GATE_KEY, token)
        payload = json.loads(decoded.payload)
        
        execution_time = datetime.now(timezone.utc).isoformat()
        receipt_hash = hashlib.sha256(f"{payload['intent_id']}-{execution_time}".encode()).hexdigest()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO forensic_audit_trail VALUES (?,?,?,?,?,?,?,?,?)",
            (payload['intent_id'], payload['agent_id'], payload['action'], payload['amount'],
             payload['approval_type'], payload['human_auditor'], payload['policy_version'], execution_time, receipt_hash))
        conn.commit()
        conn.close()

        return {"status": "executed", "forensic_hash": receipt_hash}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/audit/logs")
async def get_audit_logs():
    """Exposes the forensic trail for transparency."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM forensic_audit_trail ORDER BY executed_at DESC")
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"total_records": len(logs), "logs": logs}