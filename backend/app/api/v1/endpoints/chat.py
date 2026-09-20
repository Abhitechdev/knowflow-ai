import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import UserContext, get_current_user_context
from app.db.session import get_db
from app.models.chat import Conversation, Message, MessageSource
from app.models.feedback import Feedback
from app.models.document import Document
from app.rag.llm import RAGService
from app.schemas.chat import (
    ChatQueryRequest,
    ChatQueryResponse,
    CitationRead,
    ConversationRead,
    ConversationDetailRead,
    MessageRead,
    FeedbackCreateRequest,
    FeedbackReadResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat & RAG"])
rag_service = RAGService()


@router.post("/query", response_model=ChatQueryResponse, status_code=status.HTTP_200_OK)
async def query_knowledge_base(
    payload: ChatQueryRequest,
    user_context: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Executes a grounded question-answering query against authorized company documentation.
    Enforces server-side authorization: workspace_id, user_id, and access permissions are derived
    exclusively from the verified user_context.
    """
    clean_query = payload.message.strip()
    if not clean_query:
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")

    # 1. Resolve or create Conversation
    conversation_id = payload.conversation_id
    conversation = None
    if conversation_id:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.workspace_id == user_context.workspace_id,
        )
        res = await db.execute(stmt)
        conversation = res.scalars().first()

    if not conversation:
        # Create new conversation with title derived from user query
        conv_title = clean_query[:60] + "..." if len(clean_query) > 60 else clean_query
        conversation = Conversation(
            id=str(uuid.uuid4()),
            workspace_id=user_context.workspace_id,
            user_id=user_context.user_id,
            title=conv_title,
        )
        db.add(conversation)
        await db.flush()

    # 2. Record User Message
    user_msg_id = str(uuid.uuid4())
    user_message = Message(
        id=user_msg_id,
        conversation_id=conversation.id,
        sender_type="USER",
        content=clean_query,
    )
    db.add(user_message)
    await db.flush()

    # 3. Execute Grounded RAG Query
    rag_res = await rag_service.answer_query(
        query=clean_query,
        user_context=user_context,
        db=db,
        department_filter=payload.department_filter,
    )

    # 4. Record Assistant Message & Citations
    asst_msg_id = str(uuid.uuid4())
    asst_message = Message(
        id=asst_msg_id,
        conversation_id=conversation.id,
        sender_type="ASSISTANT",
        content=rag_res.answer,
    )
    db.add(asst_message)
    await db.flush()

    citation_reads: List[CitationRead] = []
    for cit in rag_res.citations:
        source_id = str(uuid.uuid4())
        source_record = MessageSource(
            id=source_id,
            message_id=asst_message.id,
            document_id=cit.document_id,
            chunk_id=cit.chunk_id,
            page_number=cit.page_number,
            section_heading=cit.section_heading,
            relevant_text=cit.relevant_text,
        )
        db.add(source_record)
        citation_reads.append(
            CitationRead(
                id=source_id,
                document_id=cit.document_id,
                chunk_id=cit.chunk_id,
                document_title=cit.document_title,
                page_number=cit.page_number,
                section_heading=cit.section_heading,
                relevant_text=cit.relevant_text,
                confidence=cit.confidence,
            )
        )

    await db.commit()

    grounding_status = (
        "SUFFICIENT" if rag_res.grounding_assessment.is_sufficient else "REFUSED_INSUFFICIENT_EVIDENCE"
    )

    return ChatQueryResponse(
        conversation_id=conversation.id,
        user_message_id=user_message.id,
        assistant_message_id=asst_message.id,
        query=clean_query,
        answer=rag_res.answer,
        is_grounded=rag_res.is_grounded,
        policy_applied=rag_res.policy_applied,
        citations=citation_reads,
        latency_ms=rag_res.latency_ms,
        tokens_used=rag_res.tokens_used,
        model_used=rag_res.model_used,
        grounding_status=grounding_status,
    )


@router.get("/conversations", response_model=List[ConversationRead])
async def list_conversations(
    user_context: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Lists conversations belonging to the authenticated user in the current workspace."""
    stmt = (
        select(Conversation)
        .where(
            Conversation.workspace_id == user_context.workspace_id,
            Conversation.user_id == user_context.user_id,
        )
        .order_by(desc(Conversation.updated_at))
        .limit(50)
    )
    res = await db.execute(stmt)
    convs = res.scalars().all()

    items = []
    for c in convs:
        items.append(
            ConversationRead(
                id=c.id,
                workspace_id=c.workspace_id,
                user_id=c.user_id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )
    return items


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailRead)
async def get_conversation(
    conversation_id: str,
    user_context: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full conversation with messages and verified citations."""
    stmt = (
        select(Conversation)
        .options(
            selectinload(Conversation.messages).selectinload(Message.sources)
        )
        .where(
            Conversation.id == conversation_id,
            Conversation.workspace_id == user_context.workspace_id,
        )
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    # Authorization check
    if not user_context.is_admin and conv.user_id != user_context.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to view this conversation.")

    # Map messages and citations with document title lookups
    doc_ids = set()
    for m in conv.messages:
        for s in m.sources:
            doc_ids.add(s.document_id)

    doc_title_map = {}
    if doc_ids:
        doc_stmt = select(Document.id, Document.title).where(Document.id.in_(list(doc_ids)))
        doc_res = await db.execute(doc_stmt)
        for d_id, title in doc_res.all():
            doc_title_map[d_id] = title

    msg_reads = []
    for m in sorted(conv.messages, key=lambda x: x.created_at):
        citations = []
        for s in m.sources:
            citations.append(
                CitationRead(
                    id=s.id,
                    document_id=s.document_id,
                    chunk_id=s.chunk_id,
                    document_title=doc_title_map.get(s.document_id, "Verified Document"),
                    page_number=s.page_number,
                    section_heading=s.section_heading,
                    relevant_text=s.relevant_text,
                    confidence=1.0,
                )
            )
        msg_reads.append(
            MessageRead(
                id=m.id,
                conversation_id=m.conversation_id,
                sender_type=m.sender_type,
                content=m.content,
                created_at=m.created_at,
                sources=citations,
            )
        )

    return ConversationDetailRead(
        id=conv.id,
        workspace_id=conv.workspace_id,
        user_id=conv.user_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=msg_reads,
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    user_context: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a conversation and its messages."""
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.workspace_id == user_context.workspace_id,
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()

    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    if not user_context.is_admin and conv.user_id != user_context.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this conversation.")

    await db.delete(conv)
    await db.commit()
    return None


@router.post("/feedback", response_model=FeedbackReadResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: FeedbackCreateRequest,
    user_context: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Submits positive or negative feedback on an AI answer."""
    # Verify message exists
    msg_stmt = select(Message).where(Message.id == payload.message_id)
    msg_res = await db.execute(msg_stmt)
    msg = msg_res.scalars().first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")

    rating_str = "POSITIVE" if payload.rating > 0 else "NEGATIVE"

    feedback_record = Feedback(
        id=str(uuid.uuid4()),
        message_id=payload.message_id,
        user_id=user_context.user_id,
        rating=rating_str,
        category=payload.category,
        comments=payload.comments,
    )
    db.add(feedback_record)
    await db.commit()

    return FeedbackReadResponse(
        id=feedback_record.id,
        message_id=feedback_record.message_id,
        rating=payload.rating,
        category=feedback_record.category,
        comments=feedback_record.comments,
        status="RECORDED",
    )
