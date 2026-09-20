from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class AuthUser(BaseModel):
    id: str
    email: str
    role: str = "EMPLOYEE"
    raw_user_metadata: dict[str, Any] = {}


class AuthProvider(ABC):
    """Abstract interface for authentication providers.
    Prevents hardcoding Supabase or any specific identity provider in business logic.
    """

    @abstractmethod
    async def verify_token(self, token: str) -> AuthUser | None:
        """Verifies bearer token and returns AuthUser or None."""

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Returns auth provider status and configuration state."""
