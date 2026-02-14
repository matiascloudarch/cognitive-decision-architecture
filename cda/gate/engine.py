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

SECRET_KEY_RAW = os.getenv("CDA_SECRET_KEY")
GATE_KEY = Key.new(version=4, purpose="local", key=SECRET_KEY_RAW.encode())

class Base(DeclarativeBase):
    pass

class ExecutedIntent(Base):
    __tablename__ = "executed_intents"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    entity_id: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

DATABASE_URL = "sqlite:///./cda_gate.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db

app = FastAPI(title="CDA Execution Gate API")

@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)

@app.post("/execute", status_code=status.HTTP_201_CREATED)
def execute_token(token: str, db: Annotated[Session, Depends(get_db)]):
    try:
        decoded = Paseto.new().decode(GATE_KEY, token)
        manifest = json.loads(decoded.payload)
        intent_id = manifest["intent_id"]

        # Replay Protection
        stmt = select(ExecutedIntent).where(ExecutedIntent.id == intent_id)
        if db.execute(stmt).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Intent already executed")

        # Temporal Integrity
        created_at = datetime.fromisoformat(manifest["created_at"])
        if (datetime.now(timezone.utc) - created_at).total_seconds() > manifest["ttl"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Expired")

        new_record = ExecutedIntent(id=intent_id, entity_id=manifest["entity_id"], action=manifest["action"])
        db.add(new_record)
        db.commit()

        return {"status": "success", "intent_id": intent_id}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Security Token")