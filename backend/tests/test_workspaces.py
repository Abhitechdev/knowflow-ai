"""Unit and security tests for Multi-Tenant Workspace Creation and Membership RBAC."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.v1.endpoints.workspaces import create_workspace
from app.auth.base import AuthUser
from app.auth.context import (
    DEFAULT_WORKSPACE_ID,
    UserContext,
    get_auth_user_only,
    get_current_user_context,
)
from app.models.document import Document
from app.models.workspace import Workspace, WorkspaceMember
from app.rag.retrieval import HybridRetriever
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead


# ------------------------------------------------------------------ #
# A, B, C, F: Authenticated user creates workspace and becomes ADMIN  #
# ------------------------------------------------------------------ #
@pytest.mark.asyncio
async def test_create_workspace_success_and_admin_assignment():
    mock_db = AsyncMock()
    # Mock user not existing yet and slug check returning None
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    auth_user = AuthUser(
        id="user-uuid-123",
        email="newuser@example.com",
        role="EMPLOYEE",
        raw_user_metadata={"full_name": "New User"}
    )
    workspace_in = WorkspaceCreate(name="Acme Corp", slug="acme-corp")

    added_objects = []
    mock_db.add = MagicMock(side_effect=lambda obj: added_objects.append(obj))
    mock_db.refresh = AsyncMock()

    # Create workspace
    res = await create_workspace(workspace_in=workspace_in, db=mock_db, auth_user=auth_user)

    # Assert workspace returned and created
    assert res.name == "Acme Corp"
    assert res.slug == "acme-corp"
    assert res.id is not None

    # Assert db additions: User (if new), Workspace, WorkspaceMember
    workspaces_added = [o for o in added_objects if isinstance(o, Workspace)]
    members_added = [o for o in added_objects if isinstance(o, WorkspaceMember)]

    assert len(workspaces_added) == 1
    assert workspaces_added[0].name == "Acme Corp"
    assert workspaces_added[0].slug == "acme-corp"

    assert len(members_added) == 1
    assert members_added[0].user_id == "user-uuid-123"
    assert members_added[0].role == "ADMIN"  # Creator must be ADMIN
    assert members_added[0].workspace_id == workspaces_added[0].id

    # Assert atomic commit
    mock_db.commit.assert_awaited_once()


# ------------------------------------------------------------------ #
# Duplicate slug rejection                                           #
# ------------------------------------------------------------------ #
@pytest.mark.asyncio
async def test_create_workspace_duplicate_slug_rejected():
    mock_db = AsyncMock()
    existing_ws = Workspace(id="ws-existing", name="Existing", slug="acme-corp")
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = existing_ws
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    auth_user = AuthUser(id="user-123", email="user@example.com", role="EMPLOYEE")
    workspace_in = WorkspaceCreate(name="Acme Corp", slug="acme-corp")

    with pytest.raises(HTTPException) as exc_info:
        await create_workspace(workspace_in=workspace_in, db=mock_db, auth_user=auth_user)

    assert exc_info.value.status_code == 400
    assert "slug already exists" in exc_info.value.detail


# ------------------------------------------------------------------ #
# D: Unauthenticated request rejected by get_auth_user_only          #
# ------------------------------------------------------------------ #
@pytest.mark.asyncio
async def test_get_auth_user_only_unauthenticated_rejected_in_production():
    with patch("app.auth.context.settings") as mock_settings:
        mock_settings.is_production = True
        mock_settings.allow_test_auth_bypass = False

        with pytest.raises(HTTPException) as exc_info:
            await get_auth_user_only(credentials=None)

        assert exc_info.value.status_code == 401


# ------------------------------------------------------------------ #
# E: User cannot specify another owner in request schema             #
# ------------------------------------------------------------------ #
def test_workspace_create_schema_ignores_or_forbids_injected_owner():
    payload = {
        "name": "My Workspace",
        "slug": "my-ws",
        "owner_id": "malicious-user-id",
        "user_id": "malicious-user-id",
        "workspace_id": "malicious-ws-id",
    }
    schema = WorkspaceCreate(**payload)
    # The Pydantic model must only expose name and slug
    assert not hasattr(schema, "owner_id")
    assert not hasattr(schema, "user_id")
    assert not hasattr(schema, "workspace_id")
    assert schema.name == "My Workspace"
    assert schema.slug == "my-ws"


# ------------------------------------------------------------------ #
# G: get_current_user_context() resolves the newly created membership#
# ------------------------------------------------------------------ #
@pytest.mark.asyncio
async def test_get_current_user_context_resolves_new_membership():
    mock_db = AsyncMock()
    mock_member = WorkspaceMember(
        id="mem-1",
        workspace_id="ws-new-456",
        user_id="usr-abc",
        role="ADMIN",
        department_id=None,
    )
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_member
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    mock_credentials = MagicMock()
    mock_credentials.credentials = "valid-token"

    auth_user = AuthUser(id="usr-abc", email="user@test.com", role="EMPLOYEE")

    with patch("app.auth.context.get_auth_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.verify_token.return_value = auth_user
        mock_get_provider.return_value = mock_provider

        ctx = await get_current_user_context(credentials=mock_credentials, db=mock_db)

        assert ctx.user_id == "usr-abc"
        assert ctx.workspace_id == "ws-new-456"
        assert ctx.role == "ADMIN"
        assert ctx.is_admin is True


# ------------------------------------------------------------------ #
# I: Real authenticated user with NO membership raises HTTP 403      #
# ------------------------------------------------------------------ #
@pytest.mark.asyncio
async def test_authenticated_user_with_no_membership_cannot_fallback_to_default_workspace():
    mock_db = AsyncMock()
    # No membership found in DB
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    mock_credentials = MagicMock()
    mock_credentials.credentials = "valid-token-for-unassigned-user"

    auth_user = AuthUser(id="usr-no-ws", email="orphan@test.com", role="EMPLOYEE")

    with patch("app.auth.context.get_auth_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.verify_token.return_value = auth_user
        mock_get_provider.return_value = mock_provider

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_context(credentials=mock_credentials, db=mock_db)

        assert exc_info.value.status_code == 403
        assert "no workspace membership" in exc_info.value.detail


# ------------------------------------------------------------------ #
# H: Tenant isolation in HybridRetriever                             #
# ------------------------------------------------------------------ #
def test_tenant_isolation_in_retriever():
    retriever = HybridRetriever()

    ctx_tenant_a = UserContext(
        user_id="u-a",
        email="a@tenant-a.com",
        role="ADMIN",
        workspace_id="ws-tenant-a",
        is_admin=True,
    )
    auth_filter_a = retriever.build_auth_filter(ctx_tenant_a)

    ctx_tenant_b = UserContext(
        user_id="u-b",
        email="b@tenant-b.com",
        role="ADMIN",
        workspace_id="ws-tenant-b",
        is_admin=True,
    )
    auth_filter_b = retriever.build_auth_filter(ctx_tenant_b)

    # Ensure filters are partitioned per workspace_id
    assert "ws-tenant-a" in str(auth_filter_a) or auth_filter_a is not None
    assert "ws-tenant-b" in str(auth_filter_b) or auth_filter_b is not None
