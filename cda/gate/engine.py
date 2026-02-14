import json
from datetime import datetime, timezone
from typing import Dict
from fastapi import FastAPI, HTTPException
from pyseto import Key, Paseto
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. DATABASE SETUP
Base = declarative_base()
engine = create_engine("sqlite:///./cda_gate.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ExecutedIntent(Base):
    __tablename__ = "executed_intents"
    id = Column(String, primary_key=True, index=True)
    entity_id = Column(String)
    action = Column(String)
    executed_at = Column(DateTime, default=datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

# 2. API SETUP
app = FastAPI(title="CDA Execution Gate API")
_DEV_KEY = Key.new(version=4, purpose="local", key=b"a-very-secret-key-32-chars-long-!!")

@app.post("/execute")
def execute_token(token: str):
    try:
        # Verify Token
        decoded = Paseto.new().decode(_DEV_KEY, token)
        manifest = json.loads(decoded.payload)
        
        db = SessionLocal()
        # Replay Protection
        exists = db.query(ExecutedIntent).filter(ExecutedIntent.id == manifest["intent_id"]).first()
        if exists:
            db.close()
            raise HTTPException(status_code=400, detail="Replay Attack Detected: Intent already executed")

        # Temporal Integrity
        created_at = datetime.fromisoformat(manifest["created_at"])
        if (datetime.now(timezone.utc) - created_at).total_seconds() > manifest["ttl"]:
            db.close()
            raise HTTPException(status_code=400, detail="Token Expired")

        # Record Execution
        new_exec = ExecutedIntent(
            id=manifest["intent_id"],
            entity_id=manifest["entity_id"],
            action=manifest["action"]
        )
        db.add(new_exec)
        db.commit()
        db.close()

        return {"status": "success", "action": manifest["action"], "intent_id": manifest["intent_id"]}

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=401, detail=f"Invalid Token: {str(e)}")

# Compatibility class for old tests (optional)
class GateExecutor:
    def verify_token(self, token):
        decoded = Paseto.new().decode(_DEV_KEY, token)
        return json.loads(decoded.payload)
    def execute(self, manifest):
        return True