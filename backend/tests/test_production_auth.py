"""
Tests for production authentication hardening and admin RBAC.

Gate 5B verification:
- Fail-closed authentication in production environment.
- Test-auth bypass disabled in production.
- require_admin dependency returns HTTP 403 for non-admin users.
- SecurityHeadersMiddleware adds required headers.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.auth.context import (
    DEFAULT_USER_ID,
    DEFAULT_WORKSPACE_ID,
    UserContext,
    get_current_user_context,
    require_admin,
)
from app.core.config import Settings
from fastapi import HTTPException


# ------------------------------------------------------------------ #
# Helper: build a Settings object with a given environment            #
# ------------------------------------------------------------------ #
def make_settings(env: str) -> Settings:
    return Settings(ENVIRONMENT=env, DEBUG=(env != "production"))


# ------------------------------------------------------------------ #
# Settings property tests                                             #
# ------------------------------------------------------------------ #
class TestSettingsProductionProperties:
    def test_is_production_true(self):
        s = make_settings("production")
        assert s.is_production is True

    def test_is_production_false_for_development(self):
        s = make_settings("development")
        assert s.is_production is False

    def test_allow_test_auth_bypass_false_in_production(self):
        s = make_settings("production")
        assert s.allow_test_auth_bypass is False

    def test_allow_test_auth_bypass_true_in_development(self):
        s = make_settings("development")
        assert s.allow_test_auth_bypass is True

    def test_allow_test_auth_bypass_true_in_test(self):
        s = make_settings("test")
        assert s.allow_test_auth_bypass is True


# ------------------------------------------------------------------ #
# UserContext.allowed_access_levels                                   #
# ------------------------------------------------------------------ #
class TestUserContextAccessLevels:
    def test_admin_gets_all_levels(self):
        ctx = UserContext(
            user_id="u1", email="a@test.com", role="ADMIN",
            workspace_id="ws1", is_admin=True,
        )
        levels = ctx.allowed_access_levels()
        assert "RESTRICTED" in levels
        assert "PRIVATE" in levels
        assert "PUBLIC" in levels

    def test_employee_restricted_from_confidential(self):
        ctx = UserContext(
            user_id="u2", email="b@test.com", role="EMPLOYEE",
            workspace_id="ws1", is_admin=False,
        )
        levels = ctx.allowed_access_levels()
        assert "RESTRICTED" not in levels
        assert "PRIVATE" not in levels
        assert "PUBLIC" in levels
        assert "INTERNAL" in levels

    def test_manager_gets_confidential(self):
        ctx = UserContext(
            user_id="u3", email="c@test.com", role="MANAGER",
            workspace_id="ws1", is_admin=False,
        )
        levels = ctx.allowed_access_levels()
        assert "CONFIDENTIAL" in levels
        assert "RESTRICTED" not in levels


# ------------------------------------------------------------------ #
# Fail-closed production auth                                         #
# ------------------------------------------------------------------ #
class TestProductionFailClosed:
    """Verify that missing tokens cause 401 in production."""

    @pytest.mark.asyncio
    async def test_no_token_in_production_raises_401(self):
        mock_db = AsyncMock()

        with patch("app.auth.context.settings") as mock_settings:
            mock_settings.is_production = True
            mock_settings.allow_test_auth_bypass = False

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_context(credentials=None, db=mock_db)

            assert exc_info.value.status_code == 401
            assert "Authentication required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        mock_db = AsyncMock()

        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid-token"

        with patch("app.auth.context.get_auth_provider") as mock_get_provider:
            mock_provider = AsyncMock()
            mock_provider.verify_token = AsyncMock(return_value=None)
            mock_get_provider.return_value = mock_provider

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_context(credentials=mock_credentials, db=mock_db)

            assert exc_info.value.status_code == 401
            assert "Invalid or expired" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_no_token_in_development_returns_default_context(self):
        mock_db = AsyncMock()

        with patch("app.auth.context.settings") as mock_settings:
            mock_settings.is_production = False
            mock_settings.allow_test_auth_bypass = True

            ctx = await get_current_user_context(credentials=None, db=mock_db)

        assert ctx.user_id == DEFAULT_USER_ID
        assert ctx.workspace_id == DEFAULT_WORKSPACE_ID
        assert ctx.is_admin is True


# ------------------------------------------------------------------ #
# require_admin RBAC dependency                                        #
# ------------------------------------------------------------------ #
class TestRequireAdminDependency:
    @pytest.mark.asyncio
    async def test_admin_user_passes(self):
        admin_ctx = UserContext(
            user_id="admin-1", email="admin@test.com",
            role="ADMIN", workspace_id="ws1", is_admin=True,
        )
        with patch("app.auth.context.get_current_user_context", return_value=admin_ctx):
            result = await require_admin(ctx=admin_ctx)
            assert result.is_admin is True

    @pytest.mark.asyncio
    async def test_non_admin_raises_403(self):
        employee_ctx = UserContext(
            user_id="emp-1", email="emp@test.com",
            role="EMPLOYEE", workspace_id="ws1", is_admin=False,
        )
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(ctx=employee_ctx)

        assert exc_info.value.status_code == 403
        assert "Admin role required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_manager_blocked_from_admin(self):
        manager_ctx = UserContext(
            user_id="mgr-1", email="mgr@test.com",
            role="MANAGER", workspace_id="ws1", is_admin=False,
        )
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(ctx=manager_ctx)

        assert exc_info.value.status_code == 403


# ------------------------------------------------------------------ #
# SecurityHeadersMiddleware                                           #
# ------------------------------------------------------------------ #
class TestSecurityHeadersMiddleware:
    @pytest.mark.asyncio
    async def test_security_headers_added(self):
        from app.core.security_headers import SecurityHeadersMiddleware
        from starlette.applications import Starlette
        from starlette.responses import PlainTextResponse
        from starlette.routing import Route
        from starlette.testclient import TestClient

        async def homepage(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/", homepage)])
        app.add_middleware(SecurityHeadersMiddleware)

        client = TestClient(app, raise_server_exceptions=True)
        response = client.get("/")

        assert response.status_code == 200
        assert "strict-transport-security" in response.headers
        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"
        assert "content-security-policy" in response.headers
        assert "referrer-policy" in response.headers
