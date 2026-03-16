# Regulatory Mapping & Compliance Alignment

This document details how the Cognitive Decision Architecture (CDA) maps to international regulatory frameworks and 2026 compliance deadlines.

## 🇪🇺 EU AI Act (Article 11) - Technical Documentation
The CDA ensures that high-risk AI systems maintain reconstructible audit trails.

| Requirement | CDA Implementation |
| :--- | :--- |
| **Traceability** | Every authorized action generates a SHA-256 hash binding human signature, active policy version, and normalized intent. |
| **Integrity** | Cryptographic seals ensure that documentation (Policy) matches runtime execution. |

## 🛡️ NIST AI Risk Management Framework (RMF 1.0)
CDA implements the "Measure" and "Manage" functions by separating probabilistic outcomes from deterministic gates.

- **Govern:** Structural isolation between the Agent (Reasoning) and the Kernel (Audit).
- **Measure:** Real-time validation of AI intents against hard-coded business rules ($R(I)$).
- **Manage:** Automated fail-closed logic that prevents unauthorized actions before they reach the system boundary.

## 🏦 FINRA & Financial Oversight (2026 Priorities)
Aligned with expectations for AI governance to be as robust as human-led supervisory processes.

- **Accountability:** The Reasoning entity never holds the execution key. 
- **Supervision:** The Integrity Gate acts as a digital supervisor, enforcing "Policy of Least Privilege" via PASETO v4 decision envelopes.

## 🏥 21 CFR Part 11 / GxP (Life Sciences)
Ensuring tamper-evident records for AI-driven decisions in healthcare and pharma.

- **Audit Trail:** Immutable ledger of normalzed intents, preventing "semantic drift" in forensic records.
- **Electronic Signatures:** PASETO v4 tokens bind the decision to a specific, authorized cryptographic state.
