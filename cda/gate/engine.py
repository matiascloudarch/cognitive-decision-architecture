import os
import json
from datetime import datetime, timezone
from typing import Annotated, Generator

from fastapi import FastAPI, HTTPException, Depends, status
from pyseto import Key, Paseto
from sqlalchemy import String, DateTime, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Security: Shared secret for local PASETO verification
SECRET_KEY_RAW = os.getenv("CDA_SECRET_KEY", "default-insecure-key-32-chars-!!")
GATE_KEY = Key.new(version=4, purpose="local", key=SECRET_KEY_RAW.encode())

# 1. DATABASE SCHEMA (SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass

class ExecutedIntent(Base):
    """Stores executed intent IDs to prevent Replay Attacks."""
    __tablename__ = "executed_intents"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    entity_id: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc)
    )

# 2. PERSISTENCE LAYER
DATABASE_URL = "sqlite:///./cda_gate.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency for DB session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. API INITIALIZATION
app = FastAPI(title="CDA Execution Gate API")

@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)

@app.post("/execute", status_code=status.HTTP_201_CREATED)
def execute_token(token: str, db: Annotated[Session, Depends(get_db)]):
    """
    Verifies the PASETO token and executes the contained intent if valid.
    """
    try:
        # A. Cryptographic Verification
        decoded = Paseto.new().decode(GATE_KEY, token)
        manifest = json.loads(decoded.payload)
        intent_id = manifest["intent_id"]

        # B. Replay Protection: Atomic Check in DB
        stmt = select(ExecutedIntent).where(ExecutedIntent.id == intent_id)
        if db.execute(stmt).scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Replay Attack Detected: Intent already processed"
            )

        # C. Temporal Integrity Check
        created_at = datetime.fromisoformat(manifest["created_at"])
        if (datetime.now(timezone.utc) - created_at).total_seconds() > manifest["ttl"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token Expired"
            )

        # D. Commit Execution Record
        new_record = ExecutedIntent(
            id=intent_id,
            entity_id=manifest["entity_id"],
            action=manifest["action"]
        )
        db.add(new_record)
        db.commit()

        return {
            "status": "success",
            "executed_action": manifest["action"],
            "intent_id": intent_id
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Security Token")