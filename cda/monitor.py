# cda/monitor/monitor.py
import os
import aiosqlite
import json
from datetime import datetime, timezone
from fastapi import FastAPI, BackgroundTasks
from cda.shared.models import Intent

# Initialize FastAPI app for the Security Monitor
app = FastAPI(title="CDA Security Monitor (Async)")

# Database file path
DB_PATH = "cda_audit.db"

async def init_db():
    """
    Initializes the SQLite database asynchronously.
    Creates the security_logs table if it doesn't exist.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent_id TEXT,
                action TEXT,
                entity_id TEXT,
                payload TEXT,
                timestamp TEXT
            )
        """)
        await db.commit()

@app.on_event("startup")
async def startup_event():
    """
    FastAPI startup trigger to ensure the database is ready.
    """
    await init_db()

async def log_intent_to_db(intent: Intent):
    """
    Worker function to persist intent data to SQLite without blocking the main thread.
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO security_logs (intent_id, action, entity_id, payload, timestamp) VALUES (?, ?, ?, ?, ?)",
                (
                    str(intent.id),
                    intent.action,
                    intent.entity_id,
                    intent.model_dump_json(),
                    datetime.now(timezone.utc).isoformat()
                )
            )
            await db.commit()
    except Exception as e:
        # In a real scenario, use a proper logger here
        print(f"Async Logging Error: {e}")

@app.post("/log", status_code=202)
async def log_intent(intent: Intent, background_tasks: BackgroundTasks):
    """
    Endpoint to receive logs. 
    Returns 202 Accepted immediately and delegates DB write to a background task.
    """
    background_tasks.add_task(log_intent_to_db, intent)
    return {
        "status": "logging_scheduled", 
        "intent_id": str(intent.id)
    }

@app.get("/logs")
async def get_logs():
    """
    Fetches the last 50 security logs asynchronously.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM security_logs ORDER BY id DESC LIMIT 50") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]