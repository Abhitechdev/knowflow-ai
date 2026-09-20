# Import models so they register in Base.metadata
import app.models
from app.db.base import Base


def test_schema_tables_registered():
    """Verifies that all tables specified in PRD are registered in metadata."""
    registered_tables = set(Base.metadata.tables.keys())
    expected_tables = {
        "users",
        "workspaces",
        "departments",
        "workspace_members",
        "documents",
        "document_chunks",
        "document_permissions",
        "conversations",
        "messages",
        "message_sources",
        "feedback",
        "evaluation_datasets",
        "evaluation_questions",
        "evaluation_runs",
        "audit_logs",
        "usage_events",
    }
    missing = expected_tables - registered_tables
    assert not missing, f"Missing PRD tables in metadata: {missing}"


def test_document_model_fields():
    doc_table = Base.metadata.tables["documents"]
    expected_columns = {
        "id", "workspace_id", "title", "original_filename", "file_type",
        "file_size_bytes", "storage_path", "status", "error_message",
        "access_level", "page_count", "created_at", "updated_at"
    }
    actual_columns = set(doc_table.columns.keys())
    assert expected_columns.issubset(actual_columns)


def test_document_chunk_model_fields():
    chunk_table = Base.metadata.tables["document_chunks"]
    expected_columns = {
        "id", "document_id", "workspace_id", "chunk_index", "page_number",
        "section_heading", "content", "metadata_json", "created_at"
    }
    actual_columns = set(chunk_table.columns.keys())
    assert expected_columns.issubset(actual_columns)
