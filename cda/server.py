from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from pathlib import Path
import typing
import uvicorn
import asyncio
import json
import uuid
import datetime

app = FastAPI(
    title="Cognitive Decision Architecture (CDA) API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

decision_ledger: typing.List[dict] = []
global_sequence = 0

# Numerical mapping for compatibility
VERDICT_NUMERIC_MAP = {
    "PERMITTED": 0,
    "HUMAN_REVIEW": 1,
    "DENIED": 2
}

class EvaluationRequest(BaseModel):
    agent_id: str
    jurisdiction: str
    action: str
    regime: typing.Optional[str] = "DEFAULT"
    risk_score: typing.Optional[float] = 0.0
    context: typing.Optional[dict] = None
    payload: typing.Optional[str] = None

class EvaluationResponse(BaseModel):
    verdict: str
    decision_id: str
    jurisdiction: str
    paseto_token: str
    timestamp: str

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "CDA Core API"}

@app.get("/ledger")
def get_ledger():
    return decision_ledger

@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate_action(request: EvaluationRequest):
    global global_sequence
    global_sequence += 1
    
    decision_id = f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:4]}"
    act = request.action.upper()
    
    # Deterministic policy assignment
    if act in ["DB_DROP", "POLICY_OVERRIDE", "AUTH_ELEVATION", "HUMAN_APPROVAL_REQ"]:
        verdict = "HUMAN_REVIEW"
        policy = "POL-SEC-01"
    elif act in ["ASSET_TRANSFER", "UNAUTHORIZED_ACCESS", "DENY_TEST"]:
        verdict = "DENIED"
        policy = "POL-FIN-03"
    elif act in ["READ_LOGS", "DATA_ACCESS", "DB_QUERY", "EXECUTE_TRANSACTION"]:
        verdict = "PERMITTED"
        policy = "POL-DAT-02"
    else:
        verdict = "PERMITTED" if request.risk_score < 0.7 else "DENIED"
        policy = "POL-GEN-01"

    now = datetime.datetime.now(datetime.timezone.utc)
    iso_timestamp = now.isoformat()
    jurisdiction_code = request.jurisdiction.upper()[:2]

    response_data = {
        "verdict": verdict,
        "decision_id": decision_id,
        "jurisdiction": jurisdiction_code,
        "paseto_token": f"v4.public.eyJyZWYiOiI{decision_id}…N8kQ2vH0rTz",
        "timestamp": iso_timestamp,
        "agent_id": request.agent_id,
        "action": request.action,
        "policy": policy,
        "policy_id": policy,
        "id": decision_id,
        "did": decision_id,
        "decision": verdict,
        "status": verdict,
        "agent": request.agent_id,
        "risk": request.risk_score,
        "risk_score": request.risk_score,
        "regime": request.regime,
        "created_at": iso_timestamp,
        "sequence_id": global_sequence,
        "seq": global_sequence,
        "ts": int(now.timestamp() * 1000)
    }

    decision_ledger.insert(0, response_data)
    
    return {
        "verdict": verdict,
        "decision_id": decision_id,
        "jurisdiction": jurisdiction_code,
        "paseto_token": response_data["paseto_token"],
        "timestamp": iso_timestamp
    }

@app.get("/api/v1/decisions/history")
def get_decisions_history(limit: int = 1000):
    return decision_ledger[:limit]

@app.get("/api/v1/decisions/pending")
def get_pending_decisions():
    return [d for d in decision_ledger if d.get("verdict") == "HUMAN_REVIEW" or d.get("decision") == "HUMAN_REVIEW"]

@app.post("/api/v1/decisions/{decision_id}/approve")
def approve_decision(decision_id: str):
    global global_sequence
    for item in decision_ledger:
        if item.get("decision_id") == decision_id or item.get("id") == decision_id:
            
            # Multiple-click blocking
            if item.get("verdict") != "HUMAN_REVIEW":
                return {"status": "ignored", "reason": "already_processed"}
            
            item["verdict"] = "PERMITTED"
            item["decision"] = "PERMITTED"
            item["status"] = "PERMITTED"
            
            # Force update on the stream
            global_sequence += 1
            item["sequence_id"] = global_sequence
            item["seq"] = global_sequence
            
            return {"status": "approved", "decision_id": decision_id}
    
    return {"status": "not_found", "decision_id": decision_id}

@app.post("/api/v1/decisions/{decision_id}/reject")
def reject_decision(decision_id: str):
    global global_sequence
    for item in decision_ledger:
        if item.get("decision_id") == decision_id or item.get("id") == decision_id:
            
            # Multiple-click blocking
            if item.get("verdict") != "HUMAN_REVIEW":
                return {"status": "ignored", "reason": "already_processed"}
            
            item["verdict"] = "DENIED"
            item["decision"] = "DENIED"
            item["status"] = "DENIED"
            
            # Force update on the stream
            global_sequence += 1
            item["sequence_id"] = global_sequence
            item["seq"] = global_sequence
            
            return {"status": "rejected", "decision_id": decision_id}
            
    return {"status": "not_found", "decision_id": decision_id}

@app.post("/api/v1/audit/logs")
def receive_audit_logs():
    return {"status": "acknowledged"}

@app.get("/api/v1/stream/decisions")
async def stream_decisions(request: Request, since_sequence: int = 0):
    async def event_generator():
        last_sent_seq = since_sequence
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                new_items = [d for d in decision_ledger if d.get("sequence_id", 0) > last_sent_seq]
                if new_items:
                    for item in reversed(new_items):
                        stream_item = dict(item)
                        raw_verdict = stream_item.get("verdict", "DENIED")
                        stream_item["verdict"] = VERDICT_NUMERIC_MAP.get(str(raw_verdict).upper(), 2)
                        
                        yield f"data: {json.dumps(stream_item)}\n\n"
                        last_sent_seq = max(last_sent_seq, item.get("sequence_id", 0))
                
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            # Clean disconnection handling
            pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    html_path = Path(__file__).parent / "dashboard.html"
    if not html_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Dashboard HTML file not found at: {html_path}"
        )
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run("cda.server:app", host="0.0.0.0", port=8002, reload=True)