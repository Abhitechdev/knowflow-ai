import json
import logging

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    PROJECT_NAME: str = "KnowFlow AI"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # ------------------------------------------------------------------ #
    # CORS — explicit allowlist, no wildcards in production               #
    # ------------------------------------------------------------------ #
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://knowflow-ai-pied.vercel.app",
        "https://knowflow-ai.vercel.app",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        origins = []
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    origins = json.loads(v)
                except Exception:
                    origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            else:
                origins = [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            origins = list(v)

        # Ensure core known domains and staging domains are always included
        known = [
            "https://knowflow-ai-pied.vercel.app",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        for k in known:
            if k not in origins:
                origins.append(k)

        # Normalize trailing slashes
        return [o.rstrip("/") for o in origins if o]

    # ------------------------------------------------------------------ #
    # Database                                                            #
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = ""
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # ------------------------------------------------------------------ #
    # Supabase                                                            #
    # ------------------------------------------------------------------ #
    NEXT_PUBLIC_SUPABASE_URL: str = ""
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    STORAGE_BUCKET: str = "company-documents"

    # ------------------------------------------------------------------ #
    # AI Providers                                                        #
    # ------------------------------------------------------------------ #
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ------------------------------------------------------------------ #
    # Observability / Sentry                                              #
    # ------------------------------------------------------------------ #
    SENTRY_DSN: str = ""

    # ------------------------------------------------------------------ #
    # Production auth hardening                                           #
    # When ENVIRONMENT=production the auth middleware must fail-closed.   #
    # Test-auth bypass is ONLY permitted in development/test environments.#
    # ------------------------------------------------------------------ #
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def allow_test_auth_bypass(self) -> bool:
        """Returns True ONLY in non-production environments."""
        return not self.is_production

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "backend/.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
