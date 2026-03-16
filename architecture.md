# Technical Architecture Deep Dive

## The Sovereignty Invariant
The core mathematical guarantee of CDA ensures that no decision is executed without both a policy "Yes" and a cryptographic "Seal".

$$D(I) = R(I) \cdot \Sigma$$

### Variable Definitions:
- **$D(I)$**: Final Execution Decision.
- **$R(I)$**: Deterministic Policy Result. A boolean evaluation of the normalized intent against the Policy Kernel.
- **$\Sigma$ (Sigma)**: The Sigma Seal. A cryptographic proof generated via PASETO v4 that binds the intent to a specific human/system authorization state.

## The 5-Step Execution Pipeline

### 1. Agent (Reasoning)
The AI Agent generates a raw intent based on a user prompt. This is a stochastic (probabilistic) process.

### 2. Intent Normalization
To solve the "Fuzzy-to-Fixed" problem, CDA parses the raw intent into a structured JSON schema. 
- *Example:* "Send 100 bucks to Alice" $\rightarrow$ `{ "action": "transfer", "amount": 100, "to": "Alice" }`.
- This ensures the hash is deterministic and not sensitive to minor linguistic changes.

### 3. Policy Kernel (Audit)
The normalized intent is evaluated against the current **Policy of Truth**. The Kernel returns a binary 1 (Authorized) or 0 (Denied).

### 4. Integrity Gate (The Enforcement)
The Gate verifies the **Sigma Seal**. It checks:
- Is the PASETO token valid?
- Has the policy version drifted since the intent was created?
- Is $R(I) = 1$?

### 5. Execution
Only if the Gate validates the cryptographic envelope is the payload released to the external API or database.

## Fail-Closed Design
If any part of the equation results in zero ($R(I)=0$ or $\Sigma=invalid$), the final decision $D(I)$ is mathematically forced to zero.
