# ITU-T FG-TIDA Use Case Mapping: Cognitive Decision Architecture (CDA)

## Executive Overview

The Cognitive Decision Architecture (CDA) provides a deterministic, cryptographic control plane designed to enforce real-time operational governance over autonomous AI agents. Built in alignment with ITU-T Focus Group on Trust and Identity for Humans and Agentic AI (FG-TIDA) specifications—specifically UC-4 (Dynamic Multi-Tenant Agent Governance) and UC-21 (Trust and Audit Traceability)—CDA decouples policy evaluation from operational execution.

CDA incorporates Zhao Xinghua's Two-Axis Decision Model, Cyril Gorlla's 5-State Decision Framework, and Ivan Palma's Fail-Closed Enforcement Boundary with TOCTOU context-freeze checks. Decisions are encoded within short-lived, ephemeral PASETO v4 local tokens (60-second TTL) to guarantee cryptographic non-repudiation and prevent Time-of-Check to Time-of-Use (TOCTOU) exploits.

---

## Technical Mapping to ITU-T FG-TIDA Framework

### 1. Two-Axis Decision & 5-State Governance Model

CDA integrates the core FG-TIDA governance specifications proposed by Zhao Xinghua (Two-Axis Evaluation Model) and Cyril Gorlla (5-State Decision Categorization):

* **Axis 1: Operational Action Verdict (`Axis1ActionVerdict`)**  
  Evaluates operational compliance into Cyril Gorlla's 5 discrete decision states:
  * `PERMIT`: Action complies fully with policy limits.
  * `REMEDIATE`: Action exceeds auto-approval threshold but falls within remediation boundaries. The Kernel automatically caps input parameters (e.g., amount limit) and preserves both `original_payload` and `adjusted_payload` under rule authority.
  * `ESCALATE`: Action requires Human-in-the-Loop (HITL) authorization signature.
  * `BLOCK`: Action exceeds maximum policy boundaries.
  * `INDETERMINATE`: Assigned when policy resolution is ambiguous or regime context is unregistered.

* **Axis 2: Evaluation Evidence Attestation (`Axis2EvaluationEvidence`)**  
  Provides cryptographic attestation of the policy engine's execution telemetry (Zhao Xinghua Framework):
  * Tracks execution status of the policy engine (`COMPLETE`, `INVALID_REGIME_CONTEXT`, `UNRESOLVED_DEPENDENCY_OR_STALE_CONTEXT`, `INVALID_TOKEN`, `EXPIRED_LEASE`).
  * Lists check IDs executed and explicit failure mode codes.

---

### 2. Failure Handling & Strict Regime Enforcement

To eliminate silent fallbacks (e.g., defaulting unmapped context to `FINRA_US`):
* Unregistered or unmapped `regime_context` immediately halts execution.
* The Kernel returns an `INDETERMINATE` verdict with `fallback_action: "BLOCK"` and Axis 2 status `INVALID_REGIME_CONTEXT`.
* **Zero-Token Issuance:** No PASETO v4 lease is minted, preventing downstream Gate execution.

---

### 3. Cryptographic Decision Leases (PASETO v4)

Authorization decisions are issued as PASETO v4 local tokens containing:
* `policy_ref_hash`: SHA-256 hash binding decision payload directly to policy version.
* `axis_1_action_verdict`: Complete Axis 1 state and remediation metadata.
* `axis_2_evaluation_evidence`: Verification checks and engine execution status.
* `exp`: Ephemeral 60-second lease expiration.

---

### 4. Enforcement Boundary & 3-State Execution Trace

The Gate enforces cryptographic validation and state freshness prior to target execution:
1. Validates PASETO v4 signature and lease expiration.
2. Evaluates state freshness via Iván Palma's TOCTOU context-freeze check (`global_context_freeze`).
3. Emits a deterministic 3-State Execution Trace (`EXECUTED`, `BLOCKED`, `REMEDIATED`).

---

## Regulatory and Security Standards Coverage

| Standard / Framework | Specification | CDA Implementation Boundary |
| :--- | :--- | :--- |
| **ITU-T FG-TIDA** | UC-4 & UC-21 | Two-Axis PASETO v4 tokens and 3-State execution traces |
| **ISO/IEC 42001** | Control A.6 & A.9 | Deterministic policy evaluation & audit logging |
| **EU AI Act** | High-Risk Governance | Human-in-the-Loop signature escalation |
| **OWASP Agentic AI** | ASI-001 & ASI-003 | TOCTOU freeze check & PASETO signature enforcement |