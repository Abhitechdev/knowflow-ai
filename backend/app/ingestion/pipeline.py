import logging
import os
import re
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings import get_embedding_provider
from app.ingestion.chunker import document_chunker
from app.ingestion.extractor import document_extractor
from app.models.document import Document, DocumentChunk
from app.storage.service import storage_service

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt", "md", "csv"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


def sanitize_filename(filename: str) -> str:
    """Sanitizes filename removing unsafe path traversal characters and symbols."""
    base = os.path.basename(filename)
    # Remove any dangerous characters, keep alphanumerics, dots, hyphens, underscores, spaces
    cleaned = re.sub(r"[^\w\.\-\s]", "_", base).strip()
    return cleaned or "document"


def validate_file(filename: str, content_type: str, file_size: int) -> tuple[bool, str, str]:
    """Validates file extension, size, and returns (is_valid, error_msg, sanitized_ext)."""
    if not filename:
        return False, "Filename is required.", ""

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '.{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}", ""

    if file_size <= 0:
        return False, "File is empty (0 bytes).", ext

    if file_size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE // (1024 * 1024)
        return False, f"File size ({file_size / (1024 * 1024):.1f} MB) exceeds maximum allowed size ({max_mb} MB).", ext

    return True, "", ext


async def process_document_pipeline(document_id: str, db: AsyncSession) -> Document:
    """End-to-end ingestion pipeline: Storage Download -> Extraction -> Cleaning -> Chunking -> FastEmbed -> pgvector."""
    logger.info(f"Starting ingestion pipeline for document: {document_id}")

    # Fetch document
    query = select(Document).where(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        logger.error(f"Document not found for processing: {document_id}")
        raise ValueError(f"Document {document_id} not found.")

    try:
        # Step 1: Update status to PROCESSING
        document.status = "PROCESSING"
        document.error_message = None
        await db.commit()
        await db.refresh(document)

        # Step 2: Download file bytes from Supabase Storage
        logger.info(f"Downloading file from Supabase Storage: {document.storage_path}")
        file_bytes = await storage_service.download_file(document.storage_path)

        # Step 3: Extract pages/sections
        logger.info(f"Extracting content for type '{document.file_type}' ({len(file_bytes)} bytes)")
        pages = document_extractor.extract(file_bytes, document.file_type)
        page_count = len(pages)
        logger.info(f"Extracted {page_count} page(s)/section(s) from document {document_id}")

        # Step 4: Chunk text
        chunks_data = document_chunker.chunk_document(pages)
        if not chunks_data:
            raise ValueError("No extractable text content found in document.")

        logger.info(f"Generated {len(chunks_data)} chunk(s) for document {document_id}")

        # Step 5: Clean prior chunks if re-processing
        await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))

        # Step 6: Generate Embeddings
        provider = get_embedding_provider()
        texts_to_embed = [c["content"] for c in chunks_data]
        logger.info(f"Generating {len(texts_to_embed)} vector embeddings (dim: {provider.dimension})...")
        embeddings = await provider.embed_texts(texts_to_embed)

        # Step 7: Store DocumentChunks with pgvector embeddings
        for c_data, vec in zip(chunks_data, embeddings):
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=document.id,
                workspace_id=document.workspace_id,
                chunk_index=c_data["chunk_index"],
                page_number=c_data["page_number"],
                section_heading=c_data["section_heading"],
                content=c_data["content"],
                embedding=vec,
                metadata_json="{}",
            )
            db.add(chunk)

        # Step 8: Mark Document as READY
        document.status = "READY"
        document.page_count = page_count
        document.error_message = None
        await db.commit()
        await db.refresh(document)
        logger.info(f"Document {document_id} ingestion completed successfully! Status: READY, Chunks: {len(chunks_data)}")
        return document

    except Exception as e:
        logger.exception(f"Ingestion pipeline failed for document {document_id}: {e}")
        document.status = "FAILED"
        document.error_message = str(e)[:500]
        await db.commit()
        await db.refresh(document)
        raise
