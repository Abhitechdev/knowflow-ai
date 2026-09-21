import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.auth.context import get_auth_user_only
from app.auth.base import AuthUser
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    auth_user: AuthUser = Depends(get_auth_user_only),
):
    """
    Creates a new workspace and sets the calling user as the ADMIN.
    """
    # Check if slug exists
    stmt = select(Workspace).where(Workspace.slug == workspace_in.slug)
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace slug already exists."
        )

    # Ensure user exists in users table
    stmt_user = select(User).where(User.id == auth_user.id)
    res_user = await db.execute(stmt_user)
    user = res_user.scalars().first()
    if not user:
        user = User(
            id=auth_user.id,
            email=auth_user.email,
            full_name=auth_user.raw_user_metadata.get("full_name", "") if hasattr(auth_user, "raw_user_metadata") and auth_user.raw_user_metadata else "",
            role="ADMIN",
            is_active=True,
        )
        db.add(user)

    # Create workspace
    workspace_id = str(uuid.uuid4())
    new_workspace = Workspace(
        id=workspace_id,
        name=workspace_in.name,
        slug=workspace_in.slug,
    )
    db.add(new_workspace)

    # Create membership for the user
    member_id = str(uuid.uuid4())
    new_member = WorkspaceMember(
        id=member_id,
        workspace_id=workspace_id,
        user_id=auth_user.id,
        role="ADMIN",
    )
    db.add(new_member)

    await db.commit()
    await db.refresh(new_workspace)

    return new_workspace
