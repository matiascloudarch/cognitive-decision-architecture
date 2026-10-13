# Cognitive Decision Architecture (CDA 2.0)
## Specification Draft: Two-Axis Model for Autonomous AI Agent Governance
**SPDX-License-Identifier: Apache-2.0**  
**Copyright 2026 Matias Salgado**

---

### 1. Architectural Principles
Cognitive Decision Architecture (CDA 2.0) introduces a deterministic, zero-trust control plane separating decision governance from operational boundary enforcement for autonomous agent actions.

1. **Separation of Concerns:** Policy Decision Point (Kernel) vs. Policy Enforcement Point (Gate).
2. **Two-Axis Governance Model:**
   - **Axis 1 (Remediation & Action State):** Evaluates `PERMIT`, `REMEDIATE`, `ESCALATE`, `BLOCK`, and `INDETERMINATE`.
   - **Axis 2 (Evidence & Trust Status):** Captures evaluation integrity, execution status, and check traces (`COMPLETE`, `INVALID_REGIME_CONTEXT`, `TOCTOU_STALE_CONTEXT_DETECTED`, `LEASE_EXPIRED`).
3. **Cryptographic Leases:** Short TTL (60s) PASETO v4 local tokens binding entity identity, regime policy hashes, and authorized parameters.
4. **Non-Repudiation Audit Ledger:** Append-only SHA-256 hash chaining guaranteeing historical liability attribution.

---

### 2. Boundary Enforcement Mechanisms

#### 2.1 Syntactic Payload Lock
The Enforcement Gate validates incoming execution parameters against claims cryptographically signed in the PASETO v4 token. Any parameter modification prior to downstream execution triggers an immediate `BLOCKED` trace.

#### 2.2 Behavioral Circuit Breaker
In-memory agent rate tracking halts continuous or anomalous execution bursts at the Gate boundary, preventing runaway agent loops without adding human-in-the-loop latency.

#### 2.3 Time-of-Check to Time-of-Use (TOCTOU) Protection
Context freshness is validated at execution time. When `global_context_freeze` is flagged or lease TTL expires (>60s), execution is rejected deterministically.

---

### 3. Standards Compliance
Aligned with International Telecommunication Union **ITU-T FG-TIDA Use Cases UC-4 and UC-21** for trusted AI agent execution and liability attribution.