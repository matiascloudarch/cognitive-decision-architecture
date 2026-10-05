from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path
import typing
import uvicorn

app = FastAPI(
    title="Cognitive Decision Architecture (CDA) API",
    version="1.0.0",
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated in-memory decision ledger
decision_ledger: typing.List[dict] = []

class EvaluationRequest(BaseModel):
    agent_id: str
    jurisdiction: str
    action: str
    regime: str
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
    import uuid
    import datetime
    
    # Simple deterministic risk evaluation engine logic
    decision_id = f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:4]}"
    
    if request.action in ["DB_DROP", "POLICY_OVERRIDE"]:
        verdict = "HUMAN_REVIEW"
    elif request.action == "ASSET_TRANSFER":
        verdict = "DENIED"
    else:
        verdict = "PERMITTED"

    timestamp = datetime.datetime.utcnow().strftime("%H:%M:%S")

    response_data = {
        "verdict": verdict,
        "decision_id": decision_id,
        "jurisdiction": request.jurisdiction,
        "paseto_token": f"v4.public.eyJyZWYiOiI{decision_id}…N8kQ2vH0rTz",
        "timestamp": timestamp,
        "agent_id": request.agent_id,
        "action": request.action,
    }

    # Store entry in ledger
    decision_ledger.insert(0, response_data)
    
    return response_data

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    # Resolve absolute path relative to this file location
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