import logging
import math
import re
from typing import List, Dict, Optional, Tuple
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import UserContext
from app.embeddings import get_embedding_provider
from app.models.document import Document, DocumentChunk
from app.rag.base import RankedChunk, RetrievalResult

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into lowercase terms."""
    return re.findall(r"\b\w+\b", text.lower())


STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with",
    "by", "from", "up", "about", "into", "over", "after", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "can", "could", "shall", "should", "will", "would", "may", "might", "must",
    "it", "its", "of", "who", "what", "which", "when", "where", "why", "how",
    "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t"
}


def compute_bm25_score(
    query_terms: List[str],
    doc_text: str,
    doc_len: int,
    avg_dl: float,
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    """Computes standard BM25 score for a document given query terms."""
    if not query_terms or not doc_text or avg_dl <= 0:
        return 0.0

    # Filter out stopwords so queries like 'Who won the 2022 FIFA World Cup?' don't match on 'the'
    content_terms = [t for t in query_terms if t not in STOPWORDS]
    if not content_terms:
        content_terms = query_terms

    doc_terms = _tokenize(doc_text)
    if not doc_terms:
        return 0.0

    term_freq: Dict[str, int] = {}
    for term in doc_terms:
        term_freq[term] = term_freq.get(term, 0) + 1

    score = 0.0
    for term in content_terms:
        tf = term_freq.get(term, 0)
        if tf > 0:
            numerator = tf * (k1 + 1.0)
            denominator = tf + k1 * (1.0 - b + b * (doc_len / avg_dl))
            score += numerator / denominator

    return score


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def reciprocal_rank_fusion(
    dense_ranked: List[RankedChunk],
    sparse_ranked: List[RankedChunk],
    k: int = 60,
    dense_weight: float = 0.6,
    sparse_weight: float = 0.4,
) -> List[RankedChunk]:
    """Fuses dense and sparse rankings using Reciprocal Rank Fusion (RRF).
    Formula: RRF(d) = dense_weight / (k + rank_dense) + sparse_weight / (k + rank_sparse)
    """
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, RankedChunk] = {}

    for rank, chunk in enumerate(dense_ranked, start=1):
        chunk_map[chunk.chunk_id] = chunk
        scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + (dense_weight / (k + rank))

    for rank, chunk in enumerate(sparse_ranked, start=1):
        if chunk.chunk_id not in chunk_map:
            chunk_map[chunk.chunk_id] = chunk
        scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + (sparse_weight / (k + rank))

    fused_chunks: List[RankedChunk] = []
    for chunk_id, rrf_score in sorted(scores.items(), key=lambda item: item[1], reverse=True):
        chunk = chunk_map[chunk_id]
        chunk.rrf_score = round(rrf_score, 5)
        fused_chunks.append(chunk)

    return fused_chunks


from app.rag.reranker import BaseReranker, HybridReranker, NoOpReranker


class HybridRetriever:
    """Hybrid retrieval engine combining dense vector search and sparse keyword search
    with strict server-side authorization enforcement and Stage 2 HybridReranker.
    """

    def __init__(self, top_k: int = 5, min_score_threshold: float = 0.1, use_reranker: bool = True):
        self.top_k = top_k
        self.min_score_threshold = min_score_threshold
        self.use_reranker = use_reranker
        self.reranker: BaseReranker = HybridReranker() if use_reranker else NoOpReranker()

    def build_auth_filter(self, user_context: UserContext):
        """Constructs server-side authorization SQL expressions.
        Never trust client-supplied filter parameters for permissions.
        Enforces workspace isolation, department scoping, and document clearances.
        """
        base_conditions = [
            Document.workspace_id == user_context.workspace_id,
            Document.status == "READY",
        ]

        if user_context.is_admin or user_context.role.upper() == "ADMIN":
            # Admins have full access to workspace documents
            return and_(*base_conditions)

        # Non-admins: check allowed clearances and department boundaries
        allowed_levels = user_context.allowed_access_levels()

        access_conditions = [
            and_(
                Document.access_level.in_(allowed_levels),
                or_(
                    Document.department_id.is_(None),
                    Document.department_id == user_context.department_id,
                ),
            ),
        ]
        # User's own private docs
        access_conditions.append(
            and_(
                Document.access_level == "PRIVATE",
                Document.uploaded_by_user_id == user_context.user_id,
            )
        )

        return and_(*base_conditions, or_(*access_conditions))

    async def retrieve(
        self,
        query: str,
        user_context: UserContext,
        db: AsyncSession,
        department_filter: Optional[str] = None,
    ) -> RetrievalResult:
        """Executes hybrid retrieval enforcing server-side authorization."""
        query = query.strip()
        if not query:
            return RetrievalResult(query=query, chunks=[], dense_count=0, sparse_count=0)

        # 1. Fetch authorized candidate chunks from database
        auth_condition = self.build_auth_filter(user_context)

        stmt = (
            select(DocumentChunk, Document)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(auth_condition)
        )

        # If user explicitly requests a narrower department within authorized scope
        if department_filter:
            # Only allow filtering if authorized for that department or admin
            if user_context.is_admin or user_context.department_id == department_filter:
                stmt = stmt.where(Document.department_id == department_filter)

        res = await db.execute(stmt)
        rows = res.all()

        if not rows:
            logger.info(f"No authorized documents found in workspace {user_context.workspace_id}")
            return RetrievalResult(query=query, chunks=[], dense_count=0, sparse_count=0)

        # 2. Dense Vector Scoring
        embedding_provider = get_embedding_provider()
        try:
            query_embedding = await embedding_provider.embed_query(query)
        except Exception as e:
            logger.warning(f"Failed to generate query embedding: {e}")
            query_embedding = None

        dense_candidates: List[RankedChunk] = []
        sparse_candidates: List[RankedChunk] = []

        query_terms = _tokenize(query)
        avg_doc_len = sum(len(_tokenize(chunk.content)) for chunk, _ in rows) / max(len(rows), 1)

        for chunk, doc in rows:
            # Dense calculation
            dense_score = 0.0
            if query_embedding and chunk.embedding:
                dense_score = cosine_similarity(query_embedding, chunk.embedding)

            # Sparse calculation (BM25)
            combined_text = f"{doc.title} {chunk.section_heading} {chunk.content}"
            doc_len = len(_tokenize(combined_text))
            bm25_val = compute_bm25_score(query_terms, combined_text, doc_len, avg_doc_len)
            # Normalize sparse score roughly to [0, 1]
            sparse_score = round(1.0 - (1.0 / (1.0 + bm25_val)), 4) if bm25_val > 0 else 0.0

            ranked = RankedChunk(
                chunk_id=chunk.id,
                document_id=doc.id,
                document_title=doc.title,
                file_type=doc.file_type,
                page_number=chunk.page_number,
                section_heading=chunk.section_heading or "General",
                content=chunk.content,
                dense_score=round(dense_score, 4),
                sparse_score=sparse_score,
                department_id=doc.department_id,
                access_level=doc.access_level,
            )

            if dense_score > 0.05:
                dense_candidates.append(ranked)
            if sparse_score > 0.05:
                sparse_candidates.append(ranked)

        # Sort dense and sparse candidate lists
        dense_sorted = sorted(dense_candidates, key=lambda c: c.dense_score, reverse=True)[:20]
        sparse_sorted = sorted(sparse_candidates, key=lambda c: c.sparse_score, reverse=True)[:20]

        # 3. Reciprocal Rank Fusion
        fused = reciprocal_rank_fusion(dense_sorted, sparse_sorted)

        # Filter candidates passing threshold for Stage 2 reranking
        candidates = [c for c in fused if (c.dense_score > 0.08 or c.sparse_score > 0.08)][:15]

        # 4. Stage 2 Reranking via HybridReranker
        if self.use_reranker and candidates:
            top_chunks = self.reranker.rerank(query=query, chunks=candidates, top_k=self.top_k)
        else:
            top_chunks = candidates[: self.top_k]

        return RetrievalResult(
            query=query,
            chunks=top_chunks,
            dense_count=len(dense_candidates),
            sparse_count=len(sparse_candidates),
        )
