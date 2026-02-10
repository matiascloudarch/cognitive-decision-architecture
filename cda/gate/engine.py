import json
from datetime import datetime, timezone
from typing import Dict, Set

from pyseto import Key, Paseto


# ------------------------------------------------------------------
# Key material (DEVELOPMENT / DEMO ONLY)
#
# These keys are intentionally embedded for reference purposes.
# They MUST NOT be used in production.
# In real deployments, keys are loaded from a secure KMS or HSM.
# ------------------------------------------------------------------


_DEV_PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAQkxhITk9ZWckKv+9f84GEPeX8vCGYtjHOrYMIhoFzzI=
-----END PUBLIC KEY-----"""

_PUBLIC_KEY = Key.new(
    version=4,
    purpose="public",
    key=_DEV_PUBLIC_KEY_PEM,
)


# ------------------------------------------------------------------
# Gate Executor
# ------------------------------------------------------------------

class GateExecutor:
    """
    Executes authorized actions.
    Enforces cryptographic verification and runtime safety invariants.
    """

    def __init__(self) -> None:
        self._executed_intents: Set[str] = set()

        # Stubbed state store for OCC checks
        self._state = {
            "entity-123": {
                "version": 1,
            }
        }

    # --------------------------------------------------------------

    def verify_token(self, token: str) -> Dict:
        """
        Verifies a PASETO v4.public token and returns its manifest.
        """

        try:
            parsed = Paseto.new().decode(
                _PUBLIC_KEY,
                token.encode(),
            )

            if parsed.footer != b"cda-v13.3":
                raise ValueError("Invalid token footer")

            manifest = json.loads(parsed.payload)
            return manifest

        except Exception as exc:
            raise ValueError(f"Token verification failed: {exc}") from exc

    # --------------------------------------------------------------

    def execute(self, manifest: Dict) -> None:
        """
        Executes the authorized action if all safety checks pass.
        """

        intent_id = manifest["intent_id"]
        entity_id = manifest["entity_id"]

        print(f"[Gate] Intent {intent_id}: execution requested")

        # ----------------------------------------------------------
        # TTL enforcement
        # ----------------------------------------------------------

        created_at = datetime.fromisoformat(manifest["created_at"])
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        age = (datetime.now(timezone.utc) - created_at).total_seconds()
        if age > manifest["ttl"]:
            raise ValueError("Authorization token expired")

        # ----------------------------------------------------------
        # Decision enforcement
        # ----------------------------------------------------------

        if manifest["decision"] != "allow":
            raise ValueError("Execution denied by decision")

        # ----------------------------------------------------------
        # Idempotency (replay protection)
        # ----------------------------------------------------------

        if intent_id in self._executed_intents:
            print(f"[Gate] Intent {intent_id}: already executed (SKIP)")
            return

        # ----------------------------------------------------------
        # OCC (Optimistic Concurrency Control)
        # ----------------------------------------------------------

        expected_version = manifest.get("entity_version")
        current = self._state.get(entity_id)

        if current and expected_version is not None:
            if current["version"] != expected_version:
                raise ValueError("OCC violation: state has changed")

        # ----------------------------------------------------------
        # Side effect execution (stub)
        # ----------------------------------------------------------

        print(
            f"[Gate] EXECUTING action={manifest['action']} "
            f"params={manifest['params']}"
        )

        # ----------------------------------------------------------
        # Commit execution
        # ----------------------------------------------------------

        self._executed_intents.add(intent_id)
        print(f"[Gate] Intent {intent_id}: execution committed")
