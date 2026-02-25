# CDA: Cognitive Decision Architecture
### Deterministic Governance & Forensic Auditing for AI Agents

CDA is a high-integrity framework designed to bridge the gap between autonomous AI Agent intents and corporate business rules. Unlike probabilistic governance models, CDA uses a **Deterministic Kernel** and a **Cryptographic Gate** to ensure that every AI action is authorized, audited, and traceable.

## 🚀 Key Features
- **Deterministic Governance:** Business rules are enforced via a hard-coded policy engine, preventing AI "hallucinations" from bypassing limits.
- **Cryptographic Accountability:** Uses **PASETO v4** tokens to sign decisions, ensuring non-repudiation between the Auditor (Kernel) and the Enforcer (Gate).
- **Human-in-the-Loop (HITL):** Automatic escalation to human auditors for high-risk actions (e.g., transactions exceeding thresholds).
- **Forensic Audit Trail:** Every execution generates a SHA-256 forensic hash stored in an immutable-ready ledger.

## 🏗 Architecture
1. **Kernel (The Auditor):** Evaluates agent intents against trusted context and policies. Issues signed authorization tokens.
2. **Gate (The Enforcer):** Validates tokens, checks for replay attacks (idempotency), and executes the action.
3. **Shared Models:** Pydantic-based schemas for strict data validation.

## 🛠 Tech Stack
- **Python 3.12+**
- **FastAPI** (High-performance API)
- **PySeto** (PASETO Cryptography)
- **SQLite** (Forensic Logging)

## 🚦 Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Start the Kernel: `uvicorn cda.kernel.engine:app --port 8000`
3. Start the Gate: `uvicorn cda.gate.engine:app --port 8001`