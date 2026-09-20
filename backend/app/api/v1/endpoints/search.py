import logging
import time

from app.auth.context import UserContext, get_current_user_context
from app.db.session import get_db
from app.rag.retrieval import HybridRetriever
from app.schemas.search import SearchChunkResult, SearchResponse
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def hybrid_search(
    query: str = Query(..., min_length=1, max_length=500, description="Search query string"),
    department_id: str | None = Query(None, description="Optional department filter"),
    top_k: int = Query(10, ge=1, le=50, description="Max number of results to return"),
    user_context: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Executes hybrid (dense vector + sparse BM25) search across authorized company documents.
    Server-side authorization is strictly enforced based on user_context.
    """
    start_time = time.perf_counter()

    retriever = HybridRetriever(top_k=top_k)
    retrieval_res = await retriever.retrieve(
        query=query,
        user_context=user_context,
        db=db,
        department_filter=department_id,
    )

    results = []
    for c in retrieval_res.chunks:
        # Calculate combined relevance percentage
        relevance = int(min(99, max(15, (c.dense_score * 50 + c.sparse_score * 50))))
        results.append(
            SearchChunkResult(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                document_title=c.document_title,
                file_type=c.file_type,
                page_number=c.page_number,
                section_heading=c.section_heading,
                snippet=c.content[:300] + ("..." if len(c.content) > 300 else ""),
                dense_score=c.dense_score,
                sparse_score=c.sparse_score,
                rrf_score=c.rrf_score,
                relevance_pct=relevance,
            )
        )

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return SearchResponse(
        query=query,
        total_results=len(results),
        results=results,
        latency_ms=latency_ms,
    )
