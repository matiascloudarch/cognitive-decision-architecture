# Cognitive Decision Architecture (CDA)

Reference architecture for governing autonomous agents through a strict
decision–execution split enforced by cryptographic authority.

CDA prevents runaway or unsafe agent behavior by ensuring that the component
that decides an action cannot execute it, and the component that executes an
action cannot decide it.

---

## Core Idea

Actions are only executed if accompanied by a cryptographically signed
Authority Token issued by the Decision Kernel.

The Kernel evaluates intent and context.
The Gate verifies the token and executes the side effect.
They share no memory and no implicit trust.

---

## Architecture Overview

1. An Agent proposes an Intent (untrusted).
2. The Kernel evaluates the Intent against a trusted ContextSnapshot and policy.
3. If allowed, the Kernel signs an Authority Token (PASETO v4.public).
4. The Gate verifies the token and enforces runtime safety checks.
5. Only then is the side effect executed.

---

## Key Invariants

- The Kernel never executes side effects.
- The Gate never makes authorization decisions.
- Every action requires a valid, signed Authority Token.
- Entity isolation is enforced end to end.

---

## Security Properties

- Cryptographic authorization using PASETO v4.public (Ed25519).
- Policy-as-code with explicit allow/deny rules.
- Time-bound authorization (TTL).
- Replay protection via intent idempotency.
- Optimistic concurrency control (OCC).

---

## Project Structure

```text
cda/
├── kernel/           # Decision logic, policy enforcement, token signing
├── gate/             # Token verification and execution runtime
├── shared/           # Immutable data models (Intent, ContextSnapshot)
├── context_provider/ # Interface for trusted state sources
```text

Security Notice

This repository is a reference implementation.

All cryptographic keys included in the codebase are development-only and
intentionally embedded for demonstration purposes.

Production deployments must load keys from a secure KMS or HSM and must not
embed private keys in source code.

Status

Implemented and validated reference architecture.
Not intended for direct production use.

License
Apache License 2.0