```markdown
# CDA Mapping to OWASP LLM Top 10 (Standard v1.1) 🛡️

This document provides a technical mapping of the **Cognitive Decision Architecture (CDA)** components against the **OWASP Top 10 for Large Language Model Applications**. 

The core objective of CDA is to enforce the **Sovereignty Invariant**:
> **D(I) = R(I) · Σ** > *(Decision = Reasoning × Deterministic Control)*

---

## 🏗️ Architectural Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│              COGNITIVE DECISION ARCHITECTURE (CDA)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User  →  LLM  →  Intent  →  Kernel  →  Decision  →  Ledger     │
│   |        |        |           |           |           |       │
│ [Input] [Reason] [Normalize] [Validate]  [Execute]   [Audit]    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Risk Mitigation Matrix

### LLM01: Prompt Injection
* **CDA Component:** Intent Normalization Layer
* **Control Type:** Preventive (Semantic Schema Enforcement)
* **Implementation:** Mapping stochastic language into a fixed, versioned JSON schema.
* **Technical Control:**
```yaml
normalization:
  mode: strict
  allowed_intents: ["transfer", "refund", "query", "authorize_fare"]
  schema_validation: "v2.4-stable"
  unmapped_behavior: reject_and_log
```
* **Why It Works:** By treating the LLM as an untrusted environment, CDA ensures that malicious instructions (e.g., "Ignore previous rules") never reach the Kernel because they cannot be mapped to a valid, authorized intent schema.

### LLM02: Insecure Output Handling
* **CDA Component:** Integrity Gate (The Gatekeeper)
* **Control Type:** Preventive (Cryptographic Non-Repudiation)
* **Implementation:** PASETO v4 signed tokens for all authorized executions.
* **Technical Control:**
```yaml
integrity_gate:
  signing_alg: "v4.public"
  seal_requirement: mandatory
  fail_state: fail_closed
  re_validation: true # Secondary check at system boundary
```
* **Why It Works:** The model can propose a result (like a hallucinated discount), but without a cryptographic seal from the Kernel, the system boundary will reject the execution. This was the missing link in the **Air Canada** precedent.

### LLM03: Training Data Poisoning
* **CDA Component:** Kernel Policy Versioning
* **Control Type:** Detective (Integrity Verification)
* **Implementation:** Hash verification (SHA-256) of all active business rules and policies.
* **Technical Control:**
```yaml
policy_verification:
  engine: "OPA (Open Policy Agent)"
  source_integrity: "SHA-256"
  active_hash: "7e8c...f2a1"
  auto_rollback: true
```
* **Why It Works:** Even if a model is poisoned to favor specific outcomes, the Kernel enforces external, hash-verified business rules that the model cannot alter or bypass.

### LLM04: Model Denial of Service (DoS)
* **CDA Component:** Kernel Resource Management
* **Control Type:** Preventive (FinOps Guardrails)
* **Implementation:** Multi-level rate limiting and cost budget enforcement per session.
* **Technical Control:**
```yaml
resource_limit:
  max_tokens_per_user: 50000
  cost_budget_usd: 5.00
  concurrency_limit: 2
  behavior: throttle_and_alert
```
* **Why It Works:** Governance includes availability. By enforcing limits at the Kernel level, CDA prevents resource exhaustion attacks (intentional or accidental) from impacting the infrastructure budget.

### LLM05: Supply Chain Vulnerabilities
* **CDA Component:** Ledger Provenance Tracking
* **Control Type:** Detective (Ancestry Audit)
* **Implementation:** Immutable logging of model provider, version, and metadata for every decision.
* **Technical Control:**
```yaml
provenance:
  log_model_metadata: true
  provider_verification: "signed_api_response"
  dependency_checksums: ["langchain==0.1.x", "paseto==4.x"]
```
* **Why It Works:** Provides a reconstructible audit trail. If a specific model version is compromised, the Ledger identifies every decision impacted by that specific **Rented Brain.**

### LLM06: Sensitive Data Disclosure
* **CDA Component:** Context Decoupling
* **Control Type:** Preventive (Privacy Sandbox)
* **Implementation:** Zero-Knowledge reasoning pattern where business rules are stored outside the LLM context.
* **Technical Control:**
```yaml
context_isolation:
  redaction_strategy: "pii_masking"
  external_policy_lookup: true
  send_full_policy_to_llm: false
```
* **Why It Works:** The LLM only receives the minimum context needed to reason. The actual "Law" (the policy) lives in the Kernel, invisible to the reasoning agent.

### LLM08: Excessive Agency
* **CDA Component:** Action Scope Limitation
* **Control Type:** Preventive (Boundary Enforcement)
* **Implementation:** Explicit allow-lists for external tool calls and API executions via OPA.
* **Technical Control:**
```rego
# OPA Policy Example (Rego)
default allow = false
allow {
    input.intent == "refund"
    input.amount <= 100
    input.user_role == "trusted_agent"
}
```
* **Why It Works:** Execution authority is never delegated. The LLM only has "Proposal Agency," while "Execution Authority" resides exclusively in the deterministic Kernel.

### LLM09: Overreliance (Automation Bias)
* **CDA Component:** Structural Friction + Forensic Receipt
* **Control Type:** Detective / Psychological (Accountability Link)
* **Implementation:** Mandatory human-in-the-loop for high-risk sigma (Σ) values and SHA-256 receipts.
* **Technical Control:**
```yaml
friction_layer:
  risk_threshold: 0.85
  require_signature: true
  audit_hash_algo: "SHA-256"
  receipt_output: "forensic_envelope.json"
```
* **Why It Works:** CDA introduces intentional friction for high-risk decisions. By binding a human signature to a machine proposal, we move the culture from "Trusting the AI" to **Auditing the Decision.**

---

## 📊 2026 Compliance Alignment

| Regulation / Standard | CDA Alignment Strategy | Evidence Output |
| :--- | :--- | :--- |
| **EU AI Act (Art. 11)** | High-Risk System Transparency | Reconstructible SHA-256 Ledger |
| **NIST AI RMF** | Governance & Map Functions | Deterministic Policy Kernel |
| **ISO 42001** | AI Management System (AIMS) | Immutable Audit Trail |
| **FINRA / SEC** | Algorithmic Accountability | Non-repudiation via PASETO v4 |
| **21 CFR Part 11** | Tamper-evident Records | Signed Forensic Receipts |

---

## 🚀 Implementation Checklist

1.  [ ] **Phase 1:** Deploy **Intent Normalization** to sanitize LLM stochastic output.
2.  [ ] **Phase 2:** Configure **Open Policy Agent (OPA)** as your Deterministic Kernel.
3.  [ ] **Phase 3:** Integrate **PASETO v4** for cryptographic integrity at the Gate.
4.  [ ] **Phase 4:** Enable **Immutable Ledgering** for forensic auditability and compliance.

---
*Disclaimer: CDA is an architectural framework designed to mitigate risk, not a guarantee of total security. Always perform local penetration testing on your specific implementations.*

**Version:** 1.0.0  
**License:** CC BY-SA 4.0  
**Author:** Matias Salgado
```
