"""Admin and Observability API endpoints for KnowFlow AI.
Provides system metrics, audit log feeds, and telemetry foundations.
"""

from app.auth.context import UserContext, require_admin
from app.db.session import get_db
from app.models.audit import AuditLog
from app.models.chat import Conversation, Message
from app.models.document import Document, DocumentChunk
from app.models.feedback import Feedback
from app.security.rate_limiter import rate_limit_admin
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_conversations: int
    total_messages: int
    total_audit_events: int
    positive_feedback_count: int
    negative_feedback_count: int
    grounded_answering_policy: str = "Active"
    hybrid_reranker_status: str = "Enabled"


class AuditLogItem(BaseModel):
    id: str
    workspace_id: str
    user_id: str | None = None
    action: str
    ip_address: str | None = None
    metadata_json: str
    created_at: str


@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(rate_limit_admin)])
async def get_admin_stats(
    user_context: UserContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Returns aggregated system metrics across documents, queries, and feedback."""
    doc_count = await db.scalar(select(func.count(Document.id)).where(Document.workspace_id == user_context.workspace_id)) or 0
    chunk_count = await db.scalar(select(func.count(DocumentChunk.id)).join(Document).where(Document.workspace_id == user_context.workspace_id)) or 0
    conv_count = await db.scalar(select(func.count(Conversation.id)).where(Conversation.workspace_id == user_context.workspace_id)) or 0
    msg_count = await db.scalar(select(func.count(Message.id))) or 0
    audit_count = await db.scalar(select(func.count(AuditLog.id)).where(AuditLog.workspace_id == user_context.workspace_id)) or 0

    pos_feedback = await db.scalar(select(func.count(Feedback.id)).where(Feedback.rating == "POSITIVE")) or 0
    neg_feedback = await db.scalar(select(func.count(Feedback.id)).where(Feedback.rating == "NEGATIVE")) or 0

    return AdminStatsResponse(
        total_documents=doc_count,
        total_chunks=chunk_count,
        total_conversations=conv_count,
        total_messages=msg_count,
        total_audit_events=audit_count,
        positive_feedback_count=pos_feedback,
        negative_feedback_count=neg_feedback,
        grounded_answering_policy="Active",
        hybrid_reranker_status="Enabled",
    )


@router.get("/audit-logs", response_model=list[AuditLogItem])
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    action: str | None = None,
    user_context: UserContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Returns paginated audit trails providing auditability foundations relevant to regulated environments."""
    stmt = (
        select(AuditLog)
        .where(AuditLog.workspace_id == user_context.workspace_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if action:
        stmt = stmt.where(AuditLog.action == action)

    res = await db.execute(stmt)
    rows = res.scalars().all()

    return [
        AuditLogItem(
            id=row.id,
            workspace_id=row.workspace_id,
            user_id=row.user_id,
            action=row.action,
            ip_address=row.ip_address,
            metadata_json=row.metadata_json,
            created_at=row.created_at.isoformat() if row.created_at else "",
        )
        for row in rows
    ]
