# Cognitive Decision Architecture (CDA)

A reference implementation of a secure split between **decision-making** and **action execution** for autonomous agents.

## Core Components

- **Kernel (Port 8000):** The authorization service. It validates agent intents against a trusted context and issues signed PASETO tokens.
- **Gate (Port 8001):** The execution service. It verifies tokens, enforces temporal integrity (TTL), and prevents Replay Attacks using an SQLite backend.
- **Shared Models:** Unified data structures using Pydantic for strict type validation.

## Security Features

- **Cryptographic Signing:** Uses PASETO v4 local tokens for secure communication.
- **Idempotency:** Replay protection ensures an intent is never executed twice.
- **Temporal Integrity:** Automatic expiration of authorization tokens.

## Getting Started

1. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn pyseto sqlalchemy