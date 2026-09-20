"""Unit tests for Phase 4 Granular RBAC and Document Clearance Hardening."""

from app.auth.context import UserContext
from app.rag.retrieval import HybridRetriever


def test_user_context_allowed_access_levels():
    admin = UserContext(
        user_id="u-admin",
        email="admin@test.com",
        role="ADMIN",
        workspace_id="ws-1",
        is_admin=True,
    )
    assert "CONFIDENTIAL" in admin.allowed_access_levels()
    assert "RESTRICTED" in admin.allowed_access_levels()

    compliance = UserContext(
        user_id="u-comp",
        email="comp@test.com",
        role="COMPLIANCE_OFFICER",
        workspace_id="ws-1",
        is_admin=False,
    )
    assert "CONFIDENTIAL" in compliance.allowed_access_levels()
    assert "RESTRICTED" not in compliance.allowed_access_levels()

    operator = UserContext(
        user_id="u-op",
        email="op@test.com",
        role="OPERATOR",
        workspace_id="ws-1",
        is_admin=False,
    )
    assert "PUBLIC" in operator.allowed_access_levels()
    assert "INTERNAL" in operator.allowed_access_levels()
    assert "CONFIDENTIAL" not in operator.allowed_access_levels()
    assert "RESTRICTED" not in operator.allowed_access_levels()


def test_hybrid_retriever_auth_filter_construction():
    retriever = HybridRetriever()

    admin = UserContext(
        user_id="u-admin",
        email="admin@test.com",
        role="ADMIN",
        workspace_id="ws-1",
        is_admin=True,
    )
    admin_filter = retriever.build_auth_filter(admin)
    # Admin filter should not be None
    assert admin_filter is not None

    operator = UserContext(
        user_id="u-op",
        email="op@test.com",
        role="OPERATOR",
        workspace_id="ws-1",
        department_id="QUALITY",
        is_admin=False,
    )
    op_filter = retriever.build_auth_filter(operator)
    assert op_filter is not None
