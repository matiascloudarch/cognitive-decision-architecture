# CDA: Cognitive Decision Architecture
### Deterministic Governance & Forensic Auditing for AI Agents

CDA is a high-integrity framework designed to bridge the gap between autonomous AI Agent intents and corporate business rules.

##   Key Features
- **Deterministic Governance:** Policies enforced via hard-coded rules, preventing AI "hallucinations".
- **Cryptographic Accountability:** Uses **PASETO v4** tokens for non-repudiation.
- **Human-in-the-Loop (HITL):** Escalation for high-risk actions.
- **Forensic Audit Trail:** SHA-256 forensic hashes in a tamper-evident ledger.

## 🏗 Architecture
1. **Kernel (The Auditor):** Evaluates intents against trusted policies.
2. **Gate (The Enforcer):** Validates tokens and finalizes execution.
3. **Shared Models:** Strict data validation via Pydantic.

## 🚦 Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Start Kernel: `uvicorn cda.kernel.engine:app --port 8000`
3. Start Gate: `uvicorn cda.gate.engine:app --port 8001`

## ⚖️ License
Licensed under the **Apache License, Version 2.0**. See [LICENSE](LICENSE) for details.
