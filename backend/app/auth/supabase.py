import logging
from typing import Any, Dict, Optional
import httpx
from app.auth.base import AuthProvider, AuthUser
from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseAuthProvider(AuthProvider):
    """Supabase Auth implementation conforming to AuthProvider interface."""

    def __init__(self) -> None:
        self.supabase_url = settings.NEXT_PUBLIC_SUPABASE_URL.strip()
        self.anon_key = settings.NEXT_PUBLIC_SUPABASE_ANON_KEY.strip()
        self.service_role_key = settings.SUPABASE_SERVICE_ROLE_KEY.strip()

    @property
    def is_configured(self) -> bool:
        return bool(self.supabase_url and (self.anon_key or self.service_role_key))

    async def verify_token(self, token: str) -> Optional[AuthUser]:
        if not self.is_configured or not token:
            return None

        # Verify token against Supabase Auth API
        endpoint = f"{self.supabase_url.rstrip('/')}/auth/v1/user"
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": self.anon_key or self.service_role_key,
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(endpoint, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    user_metadata = data.get("user_metadata", {})
                    return AuthUser(
                        id=data["id"],
                        email=data.get("email", ""),
                        role=user_metadata.get("role", "EMPLOYEE"),
                        raw_user_metadata=user_metadata,
                    )
        except Exception as exc:
            logger.warning(f"Supabase token verification error: {exc}")
        return None

    def get_status(self) -> Dict[str, Any]:
        if not self.is_configured:
            return {
                "provider": "supabase",
                "configured": False,
                "message": "Supabase credentials not configured in environment.",
            }
        return {
            "provider": "supabase",
            "configured": True,
            "url": self.supabase_url,
        }


_auth_provider: Optional[AuthProvider] = None


def get_auth_provider() -> AuthProvider:
    global _auth_provider
    if _auth_provider is None:
        _auth_provider = SupabaseAuthProvider()
    return _auth_provider
