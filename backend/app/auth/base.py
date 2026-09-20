from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class AuthUser(BaseModel):
    id: str
    email: str
    role: str = "EMPLOYEE"
    raw_user_metadata: Dict[str, Any] = {}


class AuthProvider(ABC):
    """Abstract interface for authentication providers.
    Prevents hardcoding Supabase or any specific identity provider in business logic.
    """

    @abstractmethod
    async def verify_token(self, token: str) -> Optional[AuthUser]:
        """Verifies bearer token and returns AuthUser or None."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Returns auth provider status and configuration state."""
        pass
