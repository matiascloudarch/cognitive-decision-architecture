import os
import sqlite3
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, status, Query
from pyseto import Key, Paseto
from dotenv import load_dotenv

load_dotenv()

# --- SECURITY VALIDATION ---
# The Gate ONLY needs the Public Key to verify the Kernel's signature.
PUBLIC_KEY_RAW = os.getenv("PASETO_PUBLIC_KEY")
if not PUBLIC_KEY_RAW:
    raise RuntimeError("CRITICAL: PASETO_PUBLIC_KEY is not defined in environment.")

GATE_VERIFICATION_KEY = Key.new(version=4, purpose="public", key=PUBLIC_KEY_RAW.encode())

app = FastAPI(title="CDA Execution Gate - Production Ready")
DB_PATH = "cda_gate.db"

def init_db():
    """Initializes the SQLite database for Replay Attack prevention."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS executed_intents (
            id TEXT PRIMARY KEY,
            entity_id TEXT,
            action TEXT,
            executed_at TIMESTAMP
        )
    """)
    conn.close()

init_db()

@app.post("/execute", status_code=status.HTTP_201_CREATED)
async def execute_action(token: str = Query(...)):
    """
    Verifies the PASETO token signature and prevents Replay Attacks.
    """
    try:
        # 1. Cryptographic Verification (V4.Public)
        # Replaces the old symmetric 'local' check.
        decoded = Paseto.decode(GATE_VERIFICATION_KEY, token) [cite: 221, 224]
        payload = json.loads(decoded.payload)
        
        intent_id = payload["intent_id"]
        
        # 2. Idempotency Check (Replay Attack Prevention)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM executed_intents WHERE id = ?", (intent_id,))
        
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=409, detail="Replay Attack Detected: Intent already executed.") [cite: 36]
            
        # 3. Log execution
        cursor.execute(
            "INSERT INTO executed_intents (id, entity_id, action, executed_at) VALUES (?, ?, ?, ?)",
            (intent_id, payload["entity_id"], payload["action"], datetime.now(timezone.utc))
        )
        conn.commit()
        conn.close()
        
        return {"status": "executed", "intent_id": intent_id}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Signature: {str(e)}") [cite: 230]