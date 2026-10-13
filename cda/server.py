# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

import asyncio
import contextlib
import datetime
import json
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from cda.gate.engine import app as gate_app

# Import CDA Two-Axis Kernel and Gate sub-applications
from cda.kernel.engine import app as kernel_app
from cda.kernel.engine import authorize_intent
from cda.shared.models import MOCK_POLICIES, AgentIntent

app = FastAPI(
    title="Cognitive Decision Architecture (CDA) Unified Control Plane API",
    version="2.0.0",
    description=(
        "Unified API merging legacy Decision Ledger stream endpoints with "
        "Two-Axis PASETO v4 Kernel and Gate enforcement."
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Kernel and Gate sub-applications under distinct routing prefixes
app.mount("/kernel", kernel_app)
app.mount("/gate", gate_app)

# JSON persistence storage path
PERSISTENCE_FILE = Path(__file__).parent / "cda_ledger.json"

# Global in-memory storage and sequence counter for real-time SSE streaming
decision_ledger: list[dict[str, Any]] = []
global_sequence = 0


def load_persisted_ledger() -> None:
    """Loads recorded decisions from local JSON persistence file if present."""
    global decision_ledger, global_sequence
    if PERSISTENCE_FILE.exists():
        try:
            with open(PERSISTENCE_FILE, encoding="utf-8") as f:
                data = json.load(f)
                decision_ledger = data.get("ledger", [])
                global_sequence = data.get("global_sequence", 0)
        except (OSError, json.JSONDecodeError):
            decision_ledger = []
            global_sequence = 0


def save_persisted_ledger() -> None:
    """Persists current decision ledger state to local JSON file."""
    with contextlib.suppress(OSError, TypeError), open(PERSISTENCE_FILE, "w", encoding="utf-8") as f:
        json.dump({"global_sequence": global_sequence, "ledger": decision_ledger}, f, indent=2)


# Initialize ledger state from disk on module load
load_persisted_ledger()

# Numerical mapping required by the UI frontend
VERDICT_NUMERIC_MAP: dict[str, int] = {
    "PERMITTED": 0,
    "PERMIT": 0,
    "HUMAN_REVIEW": 1,
    "REMEDIATE": 1,
    "ESCALATE": 1,
    "DENIED": 2,
    "BLOCK": 2,
    "INDETERMINATE": 2
}


class EvaluationRequest(BaseModel):
    """Legacy/UI evaluation request format."""
    agent_id: str
    jurisdiction: str
    action: str
    regime: Optional[str] = "FINRA_US"
    risk_score: Optional[float] = 0.0
    context: Optional[dict[str, Any]] = None
    payload: Optional[str] = None


class EvaluationResponse(BaseModel):
    """Evaluation response for the Control Plane Dashboard UI."""
    verdict: str
    decision_id: str
    jurisdiction: str
    paseto_token: str
    timestamp: str


def record_kernel_decision(audit_decision: Any, intent: AgentIntent) -> dict[str, Any]:
    """Helper function to log every Two-Axis Kernel decision into the live ledger stream."""
    global global_sequence
    global_sequence += 1

    # Map Two-Axis verdict to UI legacy strings
    if audit_decision.verdict == "PERMIT":
        ui_verdict = "PERMITTED"
        policy_id = "POL-DAT-02"
    elif audit_decision.verdict in ["ESCALATE", "REMEDIATE"]:
        ui_verdict = "HUMAN_REVIEW"
        policy_id = "POL-SEC-01"
    else:
        ui_verdict = "DENIED"
        policy_id = "POL-FIN-03"

    now = datetime.datetime.now(datetime.timezone.utc)
    iso_timestamp = now.isoformat()
    jurisdiction_code = intent.jurisdiction.upper()[:2] if intent.jurisdiction else "US"
    decision_id = f"d_{global_sequence}_{uuid.uuid4().hex[:6]}"

    token_str = audit_decision.paseto_token or f"v4.local.blocked_lease_{decision_id}"

    record: dict[str, Any] = {
        "verdict": ui_verdict,
        "decision_id": decision_id,
        "jurisdiction": jurisdiction_code,
        "country": jurisdiction_code,
        "paseto_token": token_str,
        "timestamp": iso_timestamp,
        "agent_id": intent.agent_id,
        "agent": intent.agent_id,
        "action": intent.action.upper(),
        "policy": policy_id,
        "policy_id": policy_id,
        "id": decision_id,
        "did": decision_id,
        "decision": ui_verdict,
        "status": ui_verdict,
        "risk": audit_decision.stochastic_drift_index,
        "risk_score": audit_decision.stochastic_drift_index,
        "regime": intent.regime_context,
        "created_at": iso_timestamp,
        "sequence_id": global_sequence,
        "seq": global_sequence,
        "ts": int(now.timestamp() * 1000),
        "token_verified": bool(audit_decision.paseto_token),
        "axis_1_action_verdict": audit_decision.axis_1_action_verdict.model_dump(),
        "axis_2_evaluation_evidence": audit_decision.axis_2_evaluation_evidence.model_dump()
    }

    decision_ledger.insert(0, record)
    save_persisted_ledger()
    return record


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "CDA Core API & Two-Axis Control Plane"}


@app.get("/ledger")
def get_ledger() -> list[dict[str, Any]]:
    """Returns the full decision ledger."""
    return decision_ledger


@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate_action(request: EvaluationRequest) -> dict[str, str]:
    """
    Evaluates an operational action using the Two-Axis Kernel Engine,
    generating PASETO v4 signed tokens and broadcasting updates to the SSE stream.
    """
    extracted_amount = 100.0
    if request.context and "amount" in request.context:
        with contextlib.suppress(ValueError, TypeError):
            extracted_amount = float(request.context["amount"])

    mapped_regime = request.regime.upper() if request.regime else "FINRA_US"
    if mapped_regime not in MOCK_POLICIES and mapped_regime != "DEFAULT":
        mapped_regime = "FINRA_US"

    intent = AgentIntent(
        entity_id="usr_001",
        agent_id=request.agent_id,
        action=request.action.lower(),
        params={"amount": extracted_amount},
        regime_context=mapped_regime,
        jurisdiction=request.jurisdiction
    )

    audit_decision = authorize_intent(intent=intent)
    record = record_kernel_decision(audit_decision, intent)

    return {
        "verdict": str(record["verdict"]),
        "decision_id": str(record["decision_id"]),
        "jurisdiction": str(record["jurisdiction"]),
        "paseto_token": str(record["paseto_token"]),
        "timestamp": str(record["timestamp"])
    }


@app.get("/api/v1/decisions/history")
def get_decisions_history(limit: int = 1000) -> list[dict[str, Any]]:
    """Retrieves decision history for UI dashboard initialization."""
    return decision_ledger[:limit]


@app.get("/api/v1/decisions/pending")
def get_pending_decisions() -> list[dict[str, Any]]:
    """Retrieves decisions awaiting human review."""
    return [
        d for d in decision_ledger
        if d.get("verdict") == "HUMAN_REVIEW" or d.get("decision") == "HUMAN_REVIEW"
    ]


@app.post("/api/v1/decisions/{decision_id}/approve")
def approve_decision(decision_id: str) -> dict[str, str]:
    """Approves a pending decision from the operator review queue."""
    global global_sequence
    for item in decision_ledger:
        if item.get("decision_id") == decision_id or item.get("id") == decision_id:
            if item.get("verdict") != "HUMAN_REVIEW":
                return {"status": "ignored", "reason": "already_processed"}

            item["verdict"] = "PERMITTED"
            item["decision"] = "PERMITTED"
            item["status"] = "PERMITTED"
            item["action_source"] = "HUMAN_OVERRIDE"

            global_sequence += 1
            item["sequence_id"] = global_sequence
            item["seq"] = global_sequence

            save_persisted_ledger()
            return {"status": "approved", "decision_id": decision_id}

    return {"status": "not_found", "decision_id": decision_id}


@app.post("/api/v1/decisions/{decision_id}/reject")
def reject_decision(decision_id: str) -> dict[str, str]:
    """Rejects a pending decision from the operator review queue."""
    global global_sequence
    for item in decision_ledger:
        if item.get("decision_id") == decision_id or item.get("id") == decision_id:
            if item.get("verdict") != "HUMAN_REVIEW":
                return {"status": "ignored", "reason": "already_processed"}

            item["verdict"] = "DENIED"
            item["decision"] = "DENIED"
            item["status"] = "DENIED"
            item["action_source"] = "HUMAN_OVERRIDE"

            global_sequence += 1
            item["sequence_id"] = global_sequence
            item["seq"] = global_sequence

            save_persisted_ledger()
            return {"status": "rejected", "decision_id": decision_id}

    return {"status": "not_found", "decision_id": decision_id}


@app.post("/api/v1/audit/logs")
def receive_audit_logs() -> dict[str, str]:
    """Receives client-side forensic audit logs."""
    return {"status": "acknowledged"}


@app.get("/api/v1/stream/decisions")
async def stream_decisions(request: Request, since_sequence: int = 0) -> StreamingResponse:
    """Server-Sent Events (SSE) endpoint providing real-time decision stream to UI."""
    async def event_generator() -> AsyncGenerator[str, None]:
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
            pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/", response_class=HTMLResponse)
def get_dashboard() -> str:
    """Serves the main interactive Control Plane Dashboard UI."""
    html_path = Path(__file__).parent / "index.html"
    if not html_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Dashboard HTML file not found at: {html_path}"
        )
    with open(html_path, encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    uvicorn.run("cda.server:app", host="0.0.0.0", port=8002, reload=True)