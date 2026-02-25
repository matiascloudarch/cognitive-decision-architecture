from pydantic import BaseModel
from typing import Optional, List

# Payload structure for Paseto tokens
class AuthPayload(BaseModel):
    sub: str  # Subject (user_id)
    exp: str  # Expiration
    iat: str  # Issued at
    roles: Optional[List[str]] = []