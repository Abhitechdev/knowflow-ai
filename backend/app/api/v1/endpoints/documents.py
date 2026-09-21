import logging
import uuid

from app.auth.context import UserContext, get_current_user_context
from app.db.session import get_db, get_session_factory
from app.ingestion.pipeline import (
    process_document_pipeline,
    sanitize_filename,
    validate_file,
)
from app.models.document import Document, DocumentChunk
from app.schemas.document import (
    DocumentChunkRead,
    DocumentDetailRead,
    DocumentListResponse,
    DocumentRead,
    DocumentUploadResponse,
)
from app.services.audit_service import AuditService
from app.storage.service import storage_service
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

DEFAULT_WORKSPACE_ID = "ws-default-001"
DEFAULT_USER_ID = "usr-admin-001"


async def _run_pipeline_in_background(document_id: str):
    """Background task runner with its own dedicated database session."""
    session_factory = get_session_factory()
    if not session_factory:
        logger.error("No database session factory available for background task.")
        return
    async with session_factory() as db:
        try:
            await process_document_pipeline(document_id, db)
        except Exception as e:
            logger.exception(f"Background ingestion failed for {document_id}: {e}")


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(None),
    department_id: str | None = Form(None),
    access_level: str = Form("WORKSPACE"),
    db: AsyncSession = Depends(get_db),
    user_context: UserContext = Depends(get_current_user_context),
):
    """Uploads a real document (PDF, DOCX, TXT, MD, CSV) to Supabase Storage and initiates ingestion."""
    # 1. Read file bytes
    file_bytes = await file.read()
    file_size = len(file_bytes)
    original_filename = file.filename or "uploaded_document"

    # 2. Validate file type and size
    is_valid, err_msg, ext = validate_file(original_filename, file.content_type or "", file_size)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    # 3. Clean filename and generate storage path
    clean_name = sanitize_filename(original_filename)
    doc_id = str(uuid.uuid4())
    storage_path = f"{user_context.workspace_id}/{doc_id}_{clean_name}"
    doc_title = title.strip() if title and title.strip() else original_filename

    # 4. Upload to Supabase Storage
    try:
        content_type = file.content_type or "application/octet-stream"
        await storage_service.upload_file(file_bytes, storage_path, content_type=content_type)
    except Exception as exc:
        logger.exception(f"Supabase Storage upload failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Storage upload error: {exc!s}",
        )

    # 5. Create database record
    new_doc = Document(
        id=doc_id,
        workspace_id=user_context.workspace_id,
        department_id=department_id if department_id else None,
        uploaded_by_user_id=user_context.user_id,
        title=doc_title,
        original_filename=original_filename,
        file_type=ext,
        file_size_bytes=file_size,
        storage_path=storage_path,
        status="UPLOADED",
        access_level=access_level if access_level in ("WORKSPACE", "DEPARTMENT", "PRIVATE", "ADMIN_ONLY") else "WORKSPACE",
        page_count=0,
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    # Persist audit log for upload
    await AuditService.log_event(
        db=db,
        workspace_id=user_context.workspace_id,
        action="DOCUMENT_UPLOADED",
        user_id=user_context.user_id,
        metadata={
            "document_id": doc_id,
            "title": doc_title,
            "file_type": ext,
            "file_size_bytes": file_size,
        },
    )

    # 6. Queue ingestion pipeline in background
    background_tasks.add_task(_run_pipeline_in_background, doc_id)

    doc_read = DocumentRead.model_validate(new_doc)
    doc_read.total_chunks = 0
    return DocumentUploadResponse(
        document=doc_read,
        message="Document uploaded successfully. Ingestion processing initiated in background.",
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str | None = Query(None),
    department_id: str | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user_context: UserContext = Depends(get_current_user_context),
):
    """Lists real ingested documents from the database with pagination, filters, and chunk counts."""
    base_stmt = select(Document).where(Document.workspace_id == user_context.workspace_id)

    if status:
        base_stmt = base_stmt.where(Document.status == status.upper())
    if department_id:
        base_stmt = base_stmt.where(Document.department_id == department_id)
    if search:
        search_pattern = f"%{search.strip()}%"
        base_stmt = base_stmt.where(
            (Document.title.ilike(search_pattern)) | (Document.original_filename.ilike(search_pattern))
        )

    # Count total
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    # Fetch items ordered by created_at DESC
    items_stmt = base_stmt.order_by(desc(Document.created_at)).offset(skip).limit(limit)
    items_res = await db.execute(items_stmt)
    documents = items_res.scalars().all()

    # Query chunk counts for these documents
    doc_ids = [d.id for d in documents]
    chunk_counts = {}
    if doc_ids:
        chunk_count_stmt = (
            select(DocumentChunk.document_id, func.count(DocumentChunk.id))
            .where(DocumentChunk.document_id.in_(doc_ids))
            .group_by(DocumentChunk.document_id)
        )
        chunk_res = await db.execute(chunk_count_stmt)
        for d_id, c_count in chunk_res.all():
            chunk_counts[d_id] = c_count

    items: list[DocumentRead] = []
    for d in documents:
        dr = DocumentRead.model_validate(d)
        dr.total_chunks = chunk_counts.get(d.id, 0)
        items.append(dr)

    page = (skip // limit) + 1
    return DocumentListResponse(items=items, total=total, page=page, size=limit)


@router.get("/{document_id}", response_model=DocumentDetailRead)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user_context: UserContext = Depends(get_current_user_context),
):
    """Returns detailed information for a document, including extracted chunks and signed download URL."""
    stmt = select(Document).where(Document.id == document_id, Document.workspace_id == user_context.workspace_id)
    res = await db.execute(stmt)
    document = res.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # Get chunks
    chunk_stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
    )
    chunk_res = await db.execute(chunk_stmt)
    chunks = chunk_res.scalars().all()

    # Generate temporary signed URL
    signed_url = None
    try:
        signed_url = await storage_service.get_signed_url(document.storage_path, expires_in=3600)
    except Exception as e:
        logger.warning(f"Could not generate signed URL for {document.id}: {e}")

    chunk_reads = [DocumentChunkRead.model_validate(c) for c in chunks]
    return DocumentDetailRead(
        id=document.id,
        workspace_id=document.workspace_id,
        department_id=document.department_id,
        uploaded_by_user_id=document.uploaded_by_user_id,
        title=document.title,
        original_filename=document.original_filename,
        file_type=document.file_type,
        file_size_bytes=document.file_size_bytes,
        storage_path=document.storage_path,
        status=document.status,
        error_message=document.error_message,
        access_level=document.access_level,
        page_count=document.page_count,
        total_chunks=len(chunks),
        created_at=document.created_at,
        updated_at=document.updated_at,
        chunks=chunk_reads,
        signed_url=signed_url,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user_context: UserContext = Depends(get_current_user_context),
):
    """Deletes a document from Supabase Storage and PostgreSQL."""
    stmt = select(Document).where(Document.id == document_id, Document.workspace_id == user_context.workspace_id)
    res = await db.execute(stmt)
    document = res.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    doc_id = document.id
    doc_title = document.title
    doc_storage_path = document.storage_path

    # Delete from Supabase Storage
    try:
        await storage_service.delete_file(document.storage_path)
    except Exception as e:
        logger.warning(f"Failed to delete storage file {document.storage_path}: {e}")

    # Delete from DB
    await db.delete(document)
    await db.commit()

    # Persist audit log for deletion
    await AuditService.log_event(
        db=db,
        workspace_id=user_context.workspace_id,
        action="DOCUMENT_DELETED",
        user_id=user_context.user_id,
        metadata={
            "document_id": doc_id,
            "title": doc_title,
            "storage_path": doc_storage_path,
        },
    )


@router.post("/{document_id}/retry", response_model=DocumentRead)
async def retry_document_processing(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_context: UserContext = Depends(get_current_user_context),
):
    """Retries processing for a failed document."""
    stmt = select(Document).where(Document.id == document_id, Document.workspace_id == user_context.workspace_id)
    res = await db.execute(stmt)
    document = res.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    document.status = "PROCESSING"
    document.error_message = None
    await db.commit()
    await db.refresh(document)

    background_tasks.add_task(_run_pipeline_in_background, document_id)
    dr = DocumentRead.model_validate(document)
    return dr
