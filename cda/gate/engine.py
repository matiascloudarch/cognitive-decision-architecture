import json
from datetime import datetime, timezone
from typing import Dict, Set

from pyseto import Key, Paseto

# DEVELOPMENT KEYS - DO NOT USE IN PRODUCTION
_DEV_PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAQkxhITk9ZWckKv+9f84GEPeX8vCGYtjHOrYMIhoFzzI=
-----END PUBLIC KEY-----"""

_VERIFY_KEY = Key.new(version=4, purpose="public", key=_DEV_PUBLIC_KEY_PEM)

class GateExecutor:
    """
    Invariant: The Gate does not reason about intent semantics.
    It only enforces cryptographic validity and runtime safety invariants.
    """
    def __init__(self) -> None:
        # NOTE: In-memory storage is for reference only. 
        # Production requires PostgreSQL for persistent idempotency and state.
        self._executed_intents: Set[str] = set()
        self._state = {
            "entity-123": {
                "version": 1,
                "balance": 1000,
            }
        }

    def verify_token(self, token: str) -> Dict:
        """
        Verifies PASETO v4.public integrity and returns the manifest.
        """
        try:
            parsed = Paseto.new().decode(
                _VERIFY_KEY,
                token.encode(),
            )

            if parsed.footer != b"cda-v13.3":
                raise ValueError("Invalid protocol version in token footer")

            return json.loads(parsed.payload)

        except Exception as exc:
            raise ValueError(f"Token verification failed: {exc}") from exc

    def execute(self, manifest: Dict) -> None:
        """
        Executes the authorized action after mandatory safety checks.
        """
        intent_id = manifest["intent_id"]
        entity_id = manifest["entity_id"]

        # 1. Idempotency (Replay Protection)
        if intent_id in self._executed_intents:
            return

        # 2. TTL Enforcement (Temporal Integrity)
        created_at = datetime.fromisoformat(manifest["created_at"])
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        age = (datetime.now(timezone.utc) - created_at).total_seconds()
        if age > manifest["ttl"]:
            raise ValueError("Safety Violation: Authorization token expired")

        # 3. Decision Enforcement
        if manifest["decision"] != "allow":
            raise ValueError("Execution denied by decision manifest")

        # 4. OCC (Optimistic Concurrency Control)
        current_state = self._state.get(entity_id)
        
        if current_state is None:
            raise ValueError(f"Safety Violation: Entity {entity_id} not found in Gate")

        if current_state["version"] != manifest["entity_version"]:
            raise ValueError("Conflict: State evolved before execution (OCC violation)")

        # 5. Side-effect execution (Stub for reference)
        self._apply_side_effect(manifest)

        # 6. Commit execution record
        self._executed_intents.add(intent_id)

    def _apply_side_effect(self, manifest: Dict) -> None:
        """
        Final commit to infrastructure.
        In production, this must be wrapped in a database transaction.
        """
        print(f"COMMITTED: {manifest['action']} for {manifest['entity_id']}")