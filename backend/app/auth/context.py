"""
Request-scoped user context dependency.

In PRODUCTION (settings.ENVIRONMENT == "production"):
  - Missing or invalid JWT → HTTP 401 (fail-closed).
  - Test-auth bypass defaults are NEVER applied.

In non-production environments (development, test):
  - Missing token → falls back to a default ADMIN test context
    so the dev server remains usable without Supabase credentials.
"""
import logging
import re
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.base import AuthUser
from app.auth.supabase import get_auth_provider
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember

logger = logging.getLogger(__name__)
security_scheme = HTTPBearer(auto_error=False)


class UserContext(BaseModel):
    user_id: str
    email: str
    role: str = "EMPLOYEE"  # ADMIN, MANAGER, COMPLIANCE_OFFICER, OPERATOR, AUDITOR, EMPLOYEE
    workspace_id: str
    department_id: str | None = None
    is_admin: bool = False
    clearance_level: str = "INTERNAL"  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED

    def allowed_access_levels(self) -> list[str]:
        """Returns list of document access levels this user is authorized to read."""
        if self.is_admin or self.role.upper() == "ADMIN":
            return ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED", "WORKSPACE", "DEPARTMENT", "PRIVATE"]
        if self.role.upper() in ["COMPLIANCE_OFFICER", "MANAGER"]:
            return ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "WORKSPACE", "DEPARTMENT"]
        # Standard OPERATOR / AUDITOR / EMPLOYEE
        return ["PUBLIC", "INTERNAL", "WORKSPACE", "DEPARTMENT"]


DEFAULT_WORKSPACE_ID = "ws-default-001"
DEFAULT_USER_ID = "usr-admin-001"
DEFAULT_EMAIL = "admin@knowflow.internal"


async def get_current_user_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserContext:
    """FastAPI dependency that resolves and returns the authenticated UserContext.

    Fail-closed in production: HTTP 401 if token is absent or invalid.
    Non-production: gracefully falls back to a default test context.
    """
    auth_provider = get_auth_provider()

    if credentials and credentials.credentials:
        auth_user = await auth_provider.verify_token(credentials.credentials)
        if auth_user:
            stmt = select(WorkspaceMember).where(WorkspaceMember.user_id == auth_user.id)
            res = await db.execute(stmt)
            member = res.scalars().first()

            if not member:
                # Auto-provision dedicated isolated workspace for new authenticated user
                stmt_user = select(User).where(User.id == auth_user.id)
                res_user = await db.execute(stmt_user)
                user = res_user.scalars().first()
                if not user:
                    user = User(
                        id=auth_user.id,
                        email=auth_user.email,
                        full_name=auth_user.email.split("@")[0].capitalize(),
                        role="ADMIN",
                        is_active=True,
                    )
                    db.add(user)

                clean_name = auth_user.email.split("@")[0].capitalize()
                slug_prefix = re.sub(r"[^a-z0-9]+", "-", auth_user.email.split("@")[0].lower()).strip("-") or "workspace"
                workspace_slug = f"{slug_prefix}-{auth_user.id[:8]}"

                stmt_ws = select(Workspace).where(Workspace.slug == workspace_slug)
                res_ws = await db.execute(stmt_ws)
                existing_ws = res_ws.scalars().first()
                if existing_ws:
                    workspace_id = existing_ws.id
                else:
                    workspace_id = str(uuid.uuid4())
                    new_workspace = Workspace(
                        id=workspace_id,
                        name=f"{clean_name}'s Workspace",
                        slug=workspace_slug,
                    )
                    db.add(new_workspace)

                member = WorkspaceMember(
                    id=str(uuid.uuid4()),
                    workspace_id=workspace_id,
                    user_id=auth_user.id,
                    role="ADMIN",
                )
                db.add(member)
                try:
                    await db.commit()
                except Exception as e:
                    await db.rollback()
                    logger.warning(f"Error auto-provisioning workspace for {auth_user.id}: {e}")
                    stmt_retry = select(WorkspaceMember).where(WorkspaceMember.user_id == auth_user.id)
                    res_retry = await db.execute(stmt_retry)
                    member = res_retry.scalars().first()
                    if not member:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to initialize user workspace.",
                        )

            workspace_id = member.workspace_id
            department_id = member.department_id
            role = member.role

            return UserContext(
                user_id=auth_user.id,
                email=auth_user.email,
                role=role,
                workspace_id=workspace_id,
                department_id=department_id,
                is_admin=(role.upper() == "ADMIN"),
            )

        # Token was provided but failed verification
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ------------------------------------------------------------------ #
    # No token provided                                                   #
    # ------------------------------------------------------------------ #
    if settings.is_production:
        # FAIL-CLOSED: production requires a valid token at all times.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Non-production: allow unauthenticated local dev / test access.
    if not settings.allow_test_auth_bypass:
        # Defensive: should never reach here given is_production check above.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(
        "No auth token provided — using default dev context. "
        "This code path is DISABLED in production."
    )
    return UserContext(
        user_id=DEFAULT_USER_ID,
        email=DEFAULT_EMAIL,
        role="ADMIN",
        workspace_id=DEFAULT_WORKSPACE_ID,
        department_id=None,
        is_admin=True,
    )


async def require_admin(
    ctx: UserContext = Depends(get_current_user_context),
) -> UserContext:
    """Dependency: rejects non-admin callers with HTTP 403.

    Use this on all admin-only endpoints to enforce strict RBAC.
    """
    if not ctx.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required to access this resource.",
        )
    return ctx

async def get_auth_user_only(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> AuthUser:
    """Validates JWT and returns AuthUser without requiring workspace membership."""
    auth_provider = get_auth_provider()

    if credentials and credentials.credentials:
        auth_user = await auth_provider.verify_token(credentials.credentials)
        if auth_user:
            return auth_user
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if settings.is_production:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not settings.allow_test_auth_bypass:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthUser(
        id=DEFAULT_USER_ID,
        email=DEFAULT_EMAIL,
        role="ADMIN"
    )
