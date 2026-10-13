# Regulatory Mapping & Compliance Alignment (CDA 2.0)

This document details how the Cognitive Decision Architecture (CDA 2.0) maps to international regulatory frameworks, ITU-T standards, and 2026 compliance mandates.

---

## 🇪🇺 EU AI Act (Article 11 & Article 14) - Technical Documentation & Human Oversight

The EU AI Act mandates high-risk AI systems to maintain reconstructible audit trails, strict logging, and human oversight mechanisms.

| Requirement | CDA 2.0 Implementation |
| :--- | :--- |
| **Traceability (Art. 11)** | Every authorized action generates a SHA-256 hash (`policy_ref_hash`) binding human signatures, active policy versions, and normalized intents into an immutable Ledger. |
| **Human Oversight (Art. 14)** | The Cyril Gorlla 5-State framework introduces the `ESCALATE` state, requiring a Human-in-the-Loop (`human_signature`) before a PASETO v4 lease is issued. |
| **System Integrity** | Cryptographic PASETO v4 leases ensure runtime execution exactly matches policy evaluation without parameter tampering. |

---

## 🌐 ITU-T FG-TIDA Framework (UC-4 & UC-21)

CDA 2.0 is directly aligned with the ITU-T Focus Group on Trust and Identity for Humans and Agentic AI (FG-TIDA) specifications.

| Specification | CDA 2.0 Technical Mapping |
| :--- | :--- |
| **UC-4: Dynamic Multi-Tenant Governance** | Implements Zhao Xinghua's Two-Axis Model (`Axis1ActionVerdict` and `Axis2EvaluationEvidence`) with short-lived 60-second PASETO v4 local tokens. |
| **UC-21: Trust & Audit Traceability** | The Enforcement Gate emits deterministic 3-State Execution Traces (`EXECUTED`, `BLOCKED`, `REMEDIATED`) streamed live via SSE to the Ledger and Dashboard. |
| **Strict Regime Isolation** | Unmapped or invalid regulatory regimes trigger an `INDETERMINATE` verdict with a `BLOCK` fallback, issuing zero tokens to prevent silent default bypasses. |

---

## 🛡️ NIST AI Risk Management Framework (NIST AI RMF 1.0)

CDA 2.0 operationalizes the "Govern", "Measure", and "Manage" core functions of NIST AI RMF:

* **Govern:** Strict perimeter separation where AI Agents interact solely with the Gate, keeping the Kernel, Ledger, and Dashboard inside the secure boundary.
* **Measure:** Real-time evaluation of agent intents against hard-coded policy limits, calculating stochastic drift indices in real time.
* **Manage:** Automated fail-closed execution at the Gate that blocks unauthorized or stale requests (`UNRESOLVED_DEPENDENCY_OR_STALE_CONTEXT`).

---

## 🏦 FINRA & Financial Supervisory Oversight (2026 Standards)

Meets regulatory expectations for algorithmic financial agent supervision:

* **Accountability:** Reasoning agents hold zero execution power; "Execution Authority" resides exclusively in the Gate.
* **Supervision:** The Gate acts as an automated digital supervisor, enforcing the Principle of Least Privilege via ephemeral PASETO v4 decision envelopes.
* **Remediation:** Over-limit financial transactions are automatically capped (`REMEDIATE`) preserving both original and adjusted payloads under explicit rule authority.

---

## 🏥 21 CFR Part 11 / GxP & ISO/IEC 42001 (Life Sciences & AIMS)

Ensures tamper-evident records for AI-driven decisions in healthcare, pharma, and enterprise AI management systems.

* **Audit Trail:** Immutable Ledger storing full decision history, preventing "semantic drift" in forensic records.
* **Electronic Signatures:** Ephemeral PASETO v4 tokens cryptographically bind decisions to authorized operator states and SHA-256 policy hashes.