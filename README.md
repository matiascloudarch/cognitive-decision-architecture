CDA: Cognitive Decision ArchitectureDeterministic Governance & Forensic Auditing for AI AgentsCDA is a high-integrity framework designed to bridge the gap between autonomous AI Agent intents and corporate business rules.⚖️ The Sovereignty InvariantEvery decision within the CDA framework follows a mathematical law of integrity:$$D(I) = R(I) \cdot \Sigma$$Where:D(I): Final Execution Decision.R(I): Policy Rule evaluation (Boolean/Deterministic).Σ (Sigma Seal): Cryptographic validation via PASETO v4.✨ Key FeaturesDeterministic Governance: Policies enforced via hard-coded rules, preventing AI "hallucinations".Cryptographic Accountability: Uses PASETO v4 tokens for non-repudiation.Forensic Policy Hashing: Every decision is bound to a specific, hashed version of the policy Kernel to prevent governance drift.Zero-Latency Enforcement: Policy state is sealed within the decision envelope, bypassing database bottlenecks at the execution boundary.🏗 ArchitectureKernel (The Auditor): Evaluates intents against trusted policies using immutable versioning.Gate (The Enforcer): Deterministically validates tokens and finalizes execution (Fail-closed by design).Ledger (The Forensic Record): Provides a tamper-evident audit trail with SHA-256 forensic hashes.🚦 Quick Start1. Environment SetupBash# Clone the repository
git clone https://github.com/matiascloudarch/cognitive-decision-architecture
cd cognitive-decision-architecture

# Install dependencies
pip install -r requirements.txt
2. Launching the ServicesBash# Start the Policy Kernel (Port 8000)
uvicorn cda.kernel.engine:app --port 8000

# Start the Integrity Gate (Port 8001)
uvicorn cda.gate.engine:app --port 8001
⚖️ LicenseLicensed under the Apache License, Version 2.0. See LICENSE for details.Own the decision.
