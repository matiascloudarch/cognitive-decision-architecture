# Cognitive Decision Architecture (CDA) v13.3

Reference architecture for governing autonomous agents through a strict **decision–execution split** enforced by cryptographic authority.

## Core Philosophy
CDA prevents runaway agent behavior by ensuring that the component that **decides** an action cannot **execute** it, and the component that **executes** an action cannot **decide** it. 

### Key Invariants
1. **The Kernel never executes** side effects.
2. **The Gate never reasons** about authorization.
3. **No shared memory**: Communication is strictly via signed Authority Tokens.



## 🛡️ Threat Model & Security Guarantees

| Threat | CDA Defense |
| :--- | :--- |
| **Semantic Drift** | Intent hashing and context locking at the Kernel layer. |
| **Replay Attacks** | Mandatory Idempotency check at the Gate layer. |
| **Hallucinated State** | Kernel only accepts signed ContextSnapshots from trusted providers. |
| **Runaway Execution** | Physical separation of keys. The Agent has no execution authority. |
| **Stale Authorization** | Strict TTL enforced by infrastructure clocks, not by the Agent. |

## Project Structure
- `cda/kernel/`: Stateless logic, policy enforcement, and token signing.
- `cda/gate/`: Token verification, OCC checks, and execution runtime.
- `cda/shared/`: Immutable data models (Intent, ContextSnapshot).

## Security Notice
This repository is a reference implementation. Development keys are embedded for demonstration. Production deployments **must** load keys from a secure KMS/HSM.

## License
Apache License 2.0