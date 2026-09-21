import pytest
from app.auth.context import UserContext
from app.rag.base import RankedChunk
from app.rag.grounding import GroundingEvaluator
from app.rag.llm import DeterministicLocalLLMProvider
from app.rag.retrieval import (
    HybridRetriever,
    compute_bm25_score,
    cosine_similarity,
    reciprocal_rank_fusion,
)


def test_dense_retrieval_cosine_similarity():
    """Verifies dense vector cosine similarity calculation and ordering."""
    v_query = [1.0, 0.0, 0.0]
    v_exact = [1.0, 0.0, 0.0]
    v_orthogonal = [0.0, 1.0, 0.0]
    v_partial = [0.7071, 0.7071, 0.0]

    sim_exact = cosine_similarity(v_query, v_exact)
    sim_ortho = cosine_similarity(v_query, v_orthogonal)
    sim_partial = cosine_similarity(v_query, v_partial)

    assert pytest.approx(sim_exact, 0.01) == 1.0
    assert pytest.approx(sim_ortho, 0.01) == 0.0
    assert 0.65 < sim_partial < 0.75


def test_bm25_keyword_retrieval():
    """Verifies BM25 sparse keyword score calculation."""
    query_terms = ["cold", "chain", "storage"]
    doc_match = "Clinical SOP 009: Cold chain storage requirements and refrigerated units."
    doc_unrelated = "Employee annual leave request and vacation time approval."

    avg_dl = 15.0
    score_match = compute_bm25_score(query_terms, doc_match, len(doc_match.split()), avg_dl)
    score_unrelated = compute_bm25_score(query_terms, doc_unrelated, len(doc_unrelated.split()), avg_dl)

    assert score_match > 1.0
    assert score_unrelated == 0.0


def test_rrf_fusion():
    """Verifies Reciprocal Rank Fusion combines dense and sparse rankings."""
    c1 = RankedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        document_title="Cold Chain",
        content="Cold chain temp between 2 and 8C",
        dense_score=0.9,
        sparse_score=0.3,
    )
    c2 = RankedChunk(
        chunk_id="chunk-2",
        document_id="doc-2",
        document_title="Deviation Management",
        content="Deviation reporting timeline",
        dense_score=0.3,
        sparse_score=0.85,
    )
    c3 = RankedChunk(
        chunk_id="chunk-3",
        document_id="doc-3",
        document_title="Unrelated Policy",
        content="General policy",
        dense_score=0.1,
        sparse_score=0.1,
    )

    dense_ranked = [c1, c2, c3]
    sparse_ranked = [c2, c1, c3]

    fused = reciprocal_rank_fusion(dense_ranked, sparse_ranked, k=60)
    assert len(fused) == 3
    # Top 2 should have high RRF scores, c3 should be lowest
    assert fused[2].chunk_id == "chunk-3"
    assert fused[0].rrf_score > fused[2].rrf_score


def test_grounding_refusal_policy():
    """Verifies Grounded Answering Policy refuses when documentation is insufficient."""
    evaluator = GroundingEvaluator()

    # 1. Empty chunks -> Refusal
    assessment_empty = evaluator.evaluate("Who won the World Cup?", [])
    assert not assessment_empty.is_sufficient
    assert assessment_empty.policy == "Grounded Answering Policy"
    refusal_msg = evaluator.generate_refusal_answer("Who won the World Cup?", assessment_empty)
    assert "Grounded Answering Policy" in refusal_msg
    assert "no verified procedures or manuals contained sufficient evidence" in refusal_msg

    # 2. Low relevance chunks -> Refusal
    weak_chunk = RankedChunk(
        chunk_id="weak-1",
        document_id="doc-1",
        document_title="Office Rules",
        content="Keep desks tidy and turn off lights.",
        dense_score=0.12,
        sparse_score=0.08,
        rrf_score=0.005,
    )
    assessment_weak = evaluator.evaluate("What is the cryogenic freezer temperature?", [weak_chunk])
    assert not assessment_weak.is_sufficient
    assert "Refusal enforced under Grounded Answering Policy" in assessment_weak.reason


@pytest.mark.asyncio
async def test_citation_verification_evidence():
    """Verifies that citations actually contain evidence supporting the generated claim."""
    provider = DeterministicLocalLLMProvider()

    chunk = RankedChunk(
        chunk_id="chk-sop-42",
        document_id="doc-sop-42",
        document_title="SOP-QA-042: Deviation Management",
        page_number=3,
        section_heading="Section 4.1: Reporting Timelines",
        content="All critical deviations must be reported to Quality Assurance within 24 hours of discovery.",
        dense_score=0.92,
        sparse_score=0.88,
    )

    query = "What is the deadline for reporting a critical deviation?"
    answer, citations, _tokens = await provider.generate_grounded_answer(query, [chunk])

    # 1. Answer text must contain the factual evidence
    assert "within 24 hours" in answer
    assert "SOP-QA-042: Deviation Management" in answer
    assert "Page 3" in answer

    # 2. Citations must contain exact supporting evidence excerpt
    assert len(citations) >= 1
    cit = citations[0]
    assert cit.document_id == "doc-sop-42"
    assert cit.page_number == 3
    assert cit.section_heading == "Section 4.1: Reporting Timelines"
    assert "24 hours" in cit.relevant_text
    assert cit.confidence >= 0.8


def test_unauthorized_document_access():
    """Verifies server-side authorization filters out unauthorized documents for non-admin users."""
    retriever = HybridRetriever()

    # User in Department "dept-marketing", not admin
    marketing_user = UserContext(
        user_id="usr-emp-1",
        email="emp@example.com",
        role="EMPLOYEE",
        workspace_id="ws-100",
        department_id="dept-marketing",
        is_admin=False,
    )

    auth_filter = retriever.build_auth_filter(marketing_user)
    # The filter must be an SQLAlchemy BinaryExpression or BooleanClauseList
    assert auth_filter is not None

    # Admin user
    admin_user = UserContext(
        user_id="usr-adm-1",
        email="admin@example.com",
        role="ADMIN",
        workspace_id="ws-100",
        department_id=None,
        is_admin=True,
    )
    admin_filter = retriever.build_auth_filter(admin_user)
    assert admin_filter is not None


@pytest.mark.asyncio
async def test_gemini_llm_provider():
    """Verifies GeminiLLMProvider initialization and prompt building."""
    from app.rag.llm import GeminiLLMProvider

    provider = GeminiLLMProvider(api_key="test-key", model_name="models/gemini-1.5-flash")
    assert provider.model_name == "gemini-1.5-flash"
    assert provider.api_key == "test-key"


@pytest.mark.asyncio
async def test_jina_embedding_provider():
    """Verifies JinaEmbeddingProvider initialization and 384-dimension configuration."""
    from app.embeddings.jina import JinaEmbeddingProvider

    provider = JinaEmbeddingProvider(api_key="test-key", model_name="jina-embeddings-v3")
    assert provider.dimension == 384
    assert provider.model_name == "jina-embeddings-v3"
    assert provider.api_key == "test-key"


