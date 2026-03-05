# CDA: Cognitive Decision Architecture
### Deterministic Governance & Forensic Integrity for the Agentic Era

Autonomy without control is not engineering; it’s a gamble. **CDA** is a high-integrity framework designed to bridge the gap between probabilistic AI Agent intents and deterministic corporate business rules.

## 🛡️ The Integrity Trinity
CDA enforces a strict separation of powers to ensure that no single entity can both reason and execute without independent validation:

1. **Kernel (The Auditor):** Evaluates agentic intents against immutable business policies.
2. **Gate (The Enforcer):** Deterministically enforces decisions at the system boundary.
3. **Ledger (The Forensic Record):** Provides an immutable, cryptographically sealed audit trail of every intent.

## ⚖️ The Sovereignty Invariant
Every decision within the CDA framework follows a mathematical law of integrity:

$$D(I) = R(I) \cdot \Sigma$$

Where:
- **D(I):** Final Execution Decision.
- **R(I):** Policy Rule evaluation (Boolean/Deterministic).
- **Σ (Sigma Seal):** Cryptographic validation via **PASETO v4**.

If the policy is violated or the seal is tampered with, the result is a **mathematical zero**, making unauthorized execution computationally impossible.

## ✨ Key Features
- **Deterministic Governance:** Move beyond "probabilistic monitoring" to runtime enforcement.
- **Forensic Policy Hashing:** Every decision is bound to a specific, hashed version of the policy Kernel to prevent governance drift.
- **Zero-Latency Enforcement:** Policy state is sealed within the decision envelope, bypassing database bottlenecks at the execution boundary.
- **Non-Repudiation:** Leveraging PASETO v4 for high-stakes security and verifiable accountability.
- **Forensic Ledgering:** SHA-256 anchoring of intents for post-event auditing and legal responsibility.

## 🏗 Architecture Details

### Forensic Integrity & Versioning
Unlike systems that rely on on-the-fly recompilation, CDA utilizes **Immutable Versioning**. Each policy update triggers a new Kernel hash. This ensures that the forensic audit trail can always map a specific execution back to the exact logic that authorized it at "commit time."

### Structural Isolation
The **Integrity Gate** is designed to be fail-closed by default. It remains agnostic to the AI's reasoning path, only validating the cryptographic integrity and policy compliance of the final intent envelope.

## 🚦 Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone [https://github.com/matiascloudarch/cognitive-decision-architecture](https://github.com/matiascloudarch/cognitive-decision-architecture)
cd cognitive-decision-architecture

# Install dependencies
pip install -r requirements.txt
2. Launching the Services
Bash
# Start the Policy Kernel (Port 8000)
uvicorn cda.kernel.engine:app --port 8000

# Start the Integrity Gate (Port 8001)
uvicorn cda.gate.engine:app --port 8001
⚖️ License
Licensed under the Apache License, Version 2.0. See LICENSE for details.

Own the decision.
