# Cognitive Decision Architecture (CDA 2.0)
## Specification Draft: Two-Axis Model for Autonomous AI Agent Governance
**SPDX-License-Identifier: Apache-2.0**  
**Copyright 2026 Matias Salgado**

---

### 1. Architectural Principles
Cognitive Decision Architecture (CDA 2.0) introduces a deterministic, zero-trust control plane separating decision governance from operational boundary enforcement for autonomous agent actions.

1. **Separation of Concerns:** Policy Decision Point (Kernel) vs. Policy Enforcement Point (Gate).
2. **Two-Axis Governance Model:**
   - **Axis 1 (Action Verdict):** Evaluates business intent outcomes (`PERMIT`, `REMEDIATE`, `ESCALATE`, `BLOCK`, `INDETERMINATE`).
   - **Axis 2 (Evaluation Evidence):** Captures evaluation integrity, execution status, and check traces (`PAYLOAD_VALID`, `UNMAPPED_REGIME_CONTEXT`, `TOCTOU_STALE_CONTEXT_DETECTED`, `EXPIRED_LEASE_TOKEN`).
3. **Cryptographic Leases:** Short TTL (60s) PASETO v4 local tokens (shared-key authenticated encryption) binding entity identity, policy reference hashes (`policy_ref_hash`), and authorized parameters.
4. **Audit Ledger:** Append-only SHA-256 hash-chained ledger guaranteeing historical liability attribution across three distinct layers:
   - `guard_decision`: Policy Kernel verdict and Gate attestation.
   - `attempted_action`: Raw requested intent from the AI agent.
   - `independently_observed_target_state`: Verified downstream resource state confirming zero-mutation on block.

---

### 2. Boundary Enforcement Mechanisms

#### 2.1 Syntactic Payload Lock
The Enforcement Gate validates incoming execution parameters against claims cryptographically sealed inside the PASETO v4 local token (shared-key AEAD). Any parameter modification prior to downstream execution triggers an immediate `PAYLOAD_TAMPERING_DETECTED` trace and blocks execution.

#### 2.2 Behavioral Circuit Breaker & Human-in-the-Loop
In-memory agent rate tracking halts continuous or anomalous execution loops at the Gate boundary. Out-of-bound intents transition Axis 1 to `ESCALATE` (requiring human-in-the-loop review), placing the action on `HOLD` until an authorized cryptographic signature resolves the escalation.

#### 2.3 Time-of-Check to Time-of-Use (TOCTOU) Protection
Context freshness is validated atomically at execution time (*Check-to-Act*). When `global_context_freeze` is flagged or lease TTL expires (>60s), execution is rejected deterministically with `TOCTOU_STALE_CONTEXT_DETECTED` or `EXPIRED_LEASE_TOKEN`.

#### 2.4 Fail-Closed Context Opacity
Unrecognized or opaque regime contexts deterministically yield an `INDETERMINATE` Axis 1 verdict with a mandatory `BLOCK` fallback action, logging `UNMAPPED_REGIME_CONTEXT` on Axis 2. Default policy fallbacks are strictly prohibited.

---

### 3. Standards Compliance & Schema Alignment
Aligned with International Telecommunication Union **ITU-T FG-TIDA Use Cases UC-4 and UC-21** and Schema 1.1.0 (`urn:uc4:experiment-contract:1.1.0`) for trusted AI agent execution and liability attribution.
