# Cognitive Decision Architecture (CDA)

A professional reference implementation of a secure split between **decision-making** (Kernel) and **action execution** (Gate) for autonomous systems.

## Core Concepts

- **Kernel (Port 8000):** The authorization authority. It validates agent intents against trusted state snapshots and issues signed PASETO tokens.
- **Gate (Port 8001):** The execution enforcement point. It verifies cryptographic signatures, checks for token expiration (TTL), and prevents Replay Attacks using an SQLite backend.
- **Shared Models:** Strict data structures powered by Pydantic V2 with immutability guarantees.

## Security Features

- **PASETO v4 (Local):** Secure, modern alternative to JWT with no "algorithm: none" vulnerabilities.
- **Symmetric Validation:** Both Kernel and Gate enforce strict secret key requirements (>32 chars).
- **Idempotency:** Ensures an authorized intent is never executed more than once.
- **Audit Logging:** Gate service logs execution attempts for forensics.

## Technical Setup

### 1. Installation
This project uses a standard `pyproject.toml` for dependency management. To install in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .