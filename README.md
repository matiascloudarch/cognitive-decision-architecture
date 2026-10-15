# Cognitive Decision Architecture (CDA) 2.0: Deterministic Governance & Forensic Control Plane for AI Agents 

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Description

CDA 2.0 is a sophisticated deterministic runtime control plane, meticulously designed by Matias Salgado. It serves as a critical bridge between the autonomous intents of AI agents and the stringent requirements of corporate business rules and international regulatory mandates. CDA 2.0 provides advanced capabilities for real-time network interception, secure cryptographic decision leasing, and the establishment of an immutable forensic audit trail for agentic systems, ensuring transparency, accountability, and compliance.


Every decision within CDA 2.0 adheres to a deterministic law of integrity:

$$D(I) = R(I) \cdot \Sigma$$

Where:
- **D(I):** Final Execution Decision.
- **R(I):** Policy Rule evaluation (Boolean/Deterministic).
- **Σ (Sigma Seal):** Shared-key authenticated encryption via **PASETO v4.local** (60s Ephemeral Lease).



## Key Features

- **Deterministic Governance:** Enforces business rules and regulations with predictable, auditable outcomes.
- **Real-time Network Interception:** Captures and analyzes agent intents at the network perimeter.
- **Cryptographic Decision Leasing:** Utilizes PASETO v4.local (shared-key AEAD) for secure, time-bound authorization of actions.
- **Immutable Forensic Audit Trail:** Logs all decisions, policy evaluations, and human interventions for complete traceability.
- **Two-Axis Decision Evaluation:** Implements a robust framework for action verdicts and evidence attestation.
- **5-State Decision Model:** Employs a clear categorization of decisions (PERMIT, REMEDIATE, ESCALATE, BLOCK, INDETERMINATE).
- **TOCTOU Context-Freeze Pattern:** Detects and mitigates state drift at the execution boundary.
- **Unified Control Plane:** A single API and dashboard integrates Kernel, Gate, and Audit Ledger functionalities.
- **Interactive Dashboard:** Provides real-time telemetry, risk metrics, and operator controls.
- **Containerized Deployment:** Docker and Docker Compose support for streamlined deployment.


## Standards & Governance Contributions

CDA 2.0 incorporates select normative frameworks and evaluation models proposed within the ITU-T Focus Group on Trust and Identity for Humans and Agentic AI (FG-TIDA):

- **Two-Axis Separation (Action Verdict vs. Evaluation Evidence):** Anton Sokolov (@tyche-dev, AVS-0.2) and FG-TIDA Theme #6 Task 3. Evaluates intent via Axis 1 (Action Verdict) and Axis 2 (Evidence Attestation).
- **Checks-in-Path Recording & Silent Failure Catalog:** Steven Zhao (@zhaoxinghua09-cell) and FG-TIDA Theme #4 Task 1. Formalizes execution path recording and unmapped regime failure modes under UC-4 / UC-21.
- **5-State Verdict Taxonomy:** Cyril Gorlla (@cgorlla). Implements the decision states (`PERMIT`, `REMEDIATE`, `ESCALATE` / `REQUIRES_HUMAN_REVIEW`, `BLOCK`, `INDETERMINATE`).
- **Atomic Check-to-Act (TOCTOU) Verification Boundary:** Iván Abril Palma (@dakleyer). Integrates context-freeze patterns for detecting state drift at the execution boundary.


## Table of Contents

- [ Description](#description)
- [ Key Features](#key-features)
- [ Table of Contents](#table-of-contents)
- [ Tech Stack](#tech-stack)
- [ Installation](#installation)
- [ Usage](#usage)
- [ How to Use](#how-to-use)
- [ Project Structure](#project-structure)
- [ API Reference](#api-reference)
- [ Contributing](#contributing)
- [ License](#license)
- [ Important Links](#important-links)

## Tech Stack

- **Languages:** Python, HTML, JavaScript, CSS, YAML, Markdown
- **Frameworks & Libraries:**
  - Python: FastAPI, Uvicorn, PyseTo, Python-dotenv, Ruff, Mypy, Pytest, Pytest-cov, HTTX, Aiosqlite
  - Frontend: Vue.js (implied by `index.html` structure), Bootstrap (implied CSS styling)
  - Containerization: Docker, Docker Compose
- **Database:** SQLite (via `aiosqlite` in `pyproject.toml`)

## Installation

Follow these steps to set up the Cognitive Decision Architecture environment:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/matiascloudarch/cognitive-decision-architecture
    cd cognitive-decision-architecture
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `pyproject.toml` may also contain relevant development dependencies for `ruff`, `mypy`, `pytest`, etc.)*

4.  **Docker Setup (Recommended):**
    For a fully containerized experience, use Docker Compose:
    ```bash
    docker compose up --build
    ```
    This will build the Docker images and start the `cda-control-plane` and `cda-audit` services.

## Usage

The Cognitive Decision Architecture (CDA) is designed to act as a control plane for AI agents, ensuring their actions comply with predefined rules and regulations. It intercepts agent intents, evaluates them against policies using a two-axis system (Action Verdict and Evidence Attestation), and then either permits, remediates, escalates, or blocks the action. The system also maintains an immutable audit trail.

### Core Workflow:

1.  **AI Agent Intent:** An AI agent formulates an intent (e.g., to transfer funds, access data).
2.  **CDA Kernel Evaluation:** The intent is sent to the CDA Kernel (`/kernel/authorize` endpoint), which applies policy rules and generates a PASETO v4 signed token representing the decision.
3.  **CDA Gate Enforcement:** The PASETO token is passed along with the actual execution request to the CDA Gate (`/gate/execute` endpoint). The Gate verifies the token, checks for context drift (TOCTOU), enforces circuit breakers, and performs payload integrity checks.
4.  **Execution or Block:** Based on the Gate's validation, the action is either executed, remediated (with capped parameters), or blocked.
5.  **Audit Trail:** All decisions and enforcement actions are logged in an immutable audit ledger.

## How to Use

### 1. Launch the Unified Control Plane

If not using Docker Compose, you can launch the FastAPI application directly:

```Bash
uvicorn cda.server:app --reload --port 8002
```

### 2. Access the Control Plane Dashboard

Open your web browser to the following address to access the interactive dashboard:

```bash
[http://127.0.0.1:8002/](http://127.0.0.1:8002/)
```

### 3. Run Scenario Simulations

Execute pre-defined scenarios to test various decision paths:

```bash
python -m cda.scripts.simulate_hallucination
```

### 4. Run Adversarial Security Suite

Execute automated tests to validate security and adversarial resilience:

```bash
pytest cda/tests/test_adversarial.py -v -s
```

### 5. Validate Synthetic Vectors (ITU-T FG-TIDA Compliance)

Verify adherence to specific ITU-T standards using provided test vectors:

```bash
python -m cda.scripts.validate_vectors
```

### Example API Interaction (Kernel & Gate):

**a) Authorize Intent via Kernel:**

```python
import requests

base_url = "http://127.0.0.1:8002"

intent_data = {
    "entity_id": "usr_001",
    "agent_id": "agent-007",
    "action": "transfer_funds",
    "params": {"amount": 100.0},
    "regime_context": "FINRA_US",
    "jurisdiction": "US",
}

response = requests.post(f"{base_url}/kernel/authorize", json=intent_data)
auth_result = response.json()
print(auth_result)
# Expected output: {'verdict': 'PERMIT', ... 'paseto_token': 'v4.local....'}
```

**b) Execute Action via Gate:**

```python

token = auth_result.get("paseto_token")

gate_payload = {
    "target_service": "payment_gateway",
    "action": "transfer_funds",
    "params": {"amount": 100.0},
    "global_context_freeze": False
}

exec_response = requests.post(
    f"{base_url}/gate/execute",
    json=gate_payload,
    headers={"Authorization": f"Bearer {token}"}
)
exec_result = exec_response.json()
print(exec_result)
# Expected output: {'final_state': 'EXECUTED', ...}
```

## Project Structure

```
cognitive-decision-architecture/
├── .venv/
├── cda/
│   ├── __init__.py
│   ├── context_provider/
│   │   └── __init__.py
│   ├── gate/
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── kernel/
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── ledger/
│   │   ├── __init__.py
│   │   └── audit.py
│   ├── scenarios/
│   │   ├── __init__.py
│   │   └── s4_refunds.py
│   ├── scripts/
│   │   ├── run_full_audit.sh
│   │   ├── simulate_hallucination.py
│   │   └── validate_vectors.py
│   ├── shared/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── tests/
│   │   ├── _init_.py
│   │   ├── test_adversarial.py
│   │   ├── test_audit_ledger.py
│   │   ├── test_integration.py
│   │   ├── test_logic.py
│   │   ├── test_phase1.py
│   │   ├── test_phase2.py
│   │   └── test_s4_and_features.py
│   │   └── test_two_axes_toctou.py
│   ├── index.html
│   └── server.py
├── docs/
│   ├── architecture.md
│   ├── ITU_T_FG_TIDA_USE_CASE.md
│   ├── owasp-mapping.md
│   └── regulatory-mapping.md
│   └── SPEC_DRAFT_PARIS_2026.md
├── Dockerfile
├── docker-compose.yml
├── experiment.json
├── LICENSE
├── pyproject.toml
├── pytest.ini
├── requirements.txt
└── synthetic_vectors.json
```

## API Reference

The unified control plane exposes several API endpoints:

- **`/health` (GET):** Health check for the core API.
- **`/ledger` (GET):** Retrieves the full decision ledger.
- **`/evaluate` (POST):** Evaluates an action via the Kernel, returning a simplified response.
- **`/kernel/authorize` (POST):** The primary endpoint for the Kernel to authorize intents.
- **`/gate/execute` (POST):** The primary endpoint for the Gate to enforce execution.
- **`/api/v1/decisions/history` (GET):** Fetches historical decisions.
- **`/api/v1/decisions/pending` (GET):** Retrieves decisions awaiting human review.
- **`/api/v1/decisions/{decision_id}/approve` (POST):** Approves a pending decision.
- **`/api/v1/decisions/{decision_id}/reject` (POST):** Rejects a pending decision.
- **`/api/v1/audit/logs` (POST):** Receives client-side audit logs.
- **`/api/v1/stream/decisions` (GET):** SSE stream for real-time decision updates.
- **`/` (GET):** Serves the Control Plane Dashboard UI.

*Refer to `cda/server.py` for detailed endpoint definitions and `cda/gate/engine.py` and `cda/kernel/engine.py` for sub-application endpoints.* 

## Contributing

Contributions are welcome! Please follow these guidelines:

1.  **Fork the Repository:** Create a fork of the `cognitive-decision-architecture` repository.
2.  **Create a New Branch:** Make your changes on a separate branch (`git checkout -b feature/your-feature-name`).
3.  **Commit Your Changes:** Use clear and concise commit messages.
4.  **Push to the Branch:** `git push origin feature/your-feature-name`
5.  **Open a Pull Request:** Submit a pull request to the main repository.

Please ensure your contributions adhere to the project's coding standards and include relevant tests.

## License

This project is licensed under the **Apache License, Version 2.0**. See the `LICENSE` file for more details.


## Important Links

- **Local Control Plane Dashboard:** [http://127.0.0.1:8002/](http://127.0.0.1:8002/)
- **Author Profile:** [matiascloudarch on GitHub](https://github.com/matiascloudarch)
- **Related Standards:** [ITU-T FG-TIDA](https://www.itu.int/en/ITU-T/focusgroups/ida/Pages/default.aspx)
- **Architecture Specifications:** [Architecture Specifications](./docs/architecture.md)
- **Regulatory Alignment:** [Regulatory Alignment](./docs/regulatory-mapping.md)
- **ITU-T FG-TIDA Use Case Mapping:** [ITU-T FG-TIDA Use Case Mapping](./docs/ITU_T_FG_TIDA_USE_CASE.md)
- **OWASP LLM Top 10 Mapping:** [OWASP LLM Top 10 Mapping](./docs/owasp-mapping.md)


---
© 2026 **Cognitive Decision Architecture** | Developed by Matias Salgado

Repository: [matiascloudarch/cognitive-decision-architecture](https://github.com/matiascloudarch/cognitive-decision-architecture)

