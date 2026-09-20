"""Audit Logging Service for KnowFlow AI.
Provides auditability foundations relevant to regulated environments.
Persists immutable audit events to audit_logs table.
"""

import json
import logging
import uuid
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog

logger = logging.getLogger("knowflow.audit")


class AuditService:
    """Records audit logs for user queries, citations, access denials, and security alerts."""

    @staticmethod
    async def log_event(
        db: AsyncSession,
        workspace_id: str,
        action: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[AuditLog]:
        """Creates an audit log entry in the database and emits a structured JSON log."""
        meta_dict = metadata or {}
        meta_str = json.dumps(meta_dict)

        # Log structured JSON
        logger.info(
            "AUDIT_EVENT",
            extra={
                "audit_action": action,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "ip_address": ip_address,
                "metadata": meta_dict,
            },
        )

        try:
            audit_entry = AuditLog(
                id=str(uuid.uuid4()),
                workspace_id=workspace_id,
                user_id=user_id,
                action=action,
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else None,
                metadata_json=meta_str,
            )
            db.add(audit_entry)
            await db.commit()
            return audit_entry
        except Exception as e:
            logger.error(f"Failed to persist audit log to database: {e}")
            await db.rollback()
            return None
