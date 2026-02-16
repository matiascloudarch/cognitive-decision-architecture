# cda/gate/engine.py

import os
from typing import Any, Dict, Optional
from datetime import datetime, timedelta, timezone

# Flexible imports to handle different pyseto versions
try:
    from pyseto import Paseto, PasetoMessage, Token
except ImportError:
    # Fallback for newer or different versions
    from pyseto import Paseto, Token
    PasetoMessage = Any 

class PasetoEngine:
    """
    PASETO (Platform-Agnostic Security Tokens) Engine for secure communication.
    Uses V4.Public for asymmetric signing.
    """

    def __init__(self):
        # In a real app, load these from secure env vars or KMS
        self.private_key_pem = os.getenv("PASETO_PRIVATE_KEY", "")
        self.public_key_pem = os.getenv("PASETO_PUBLIC_KEY", "")
        self.version = "v4"
        self.purpose = "public"

    def generate_token(self, payload: Dict[str, Any], expires_in_minutes: int = 60) -> str:
        """
        Generates a signed PASETO token.
        """
        if not self.private_key_pem:
            raise ValueError("Private key is not configured")

        # Set expiration
        expiration = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        payload["exp"] = expiration.isoformat()
        
        # Create token
        token = Paseto.encode(
            key=self.private_key_pem,
            payload=payload,
            footer={"version": "1.0"},
            exp=expires_in_minutes * 60 # some versions use seconds
        )
        
        return token.decode("utf-8") if isinstance(token, bytes) else token

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verifies and decodes a PASETO token.
        """
        if not self.public_key_pem:
            raise ValueError("Public key is not configured")

        try:
            decoded = Paseto.decode(
                token,
                keys=self.public_key_pem
            )
            # Handle different return types from pyseto versions
            if hasattr(decoded, "payload"):
                return decoded.payload
            return decoded
        except Exception as e:
            raise ValueError(f"Invalid or expired token: {str(e)}")

# Global instance
paseto_engine = PasetoEngine()