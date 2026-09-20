"""Unit tests for Stage 2 HybridReranker and QueryRewriter."""

from app.rag.base import RankedChunk
from app.rag.reranker import HybridReranker, NoOpReranker
from app.rag.rewriter import MessageContext, QueryRewriter


def test_hybrid_reranker_numerical_specification_boost():
    reranker = HybridReranker()
    query = "What temperature range is required for cold chain storage?"

    chunk_title = RankedChunk(
        chunk_id="chk-001",
        document_id="doc-001",
        document_title="CLIN-SOP-009",
        page_number=1,
        section_heading="Overview",
        content="This document covers general refrigerated cold chain overview and background.",
        dense_score=0.8,
        sparse_score=0.7,
        rrf_score=0.015,
    )

    chunk_operative = RankedChunk(
        chunk_id="chk-002",
        document_id="doc-001",
        document_title="CLIN-SOP-009",
        page_number=2,
        section_heading="1. Temperature Specifications and Monitoring",
        content="Refrigerated Storage: Controlled between +2.0°C and +8.0°C. Deep Frozen: -20.0°C ± 5°C.",
        dense_score=0.75,
        sparse_score=0.65,
        rrf_score=0.014,
    )

    reranked = reranker.rerank(query=query, chunks=[chunk_title, chunk_operative], top_k=2)

    assert len(reranked) == 2
    # The operative section containing '+2.0°C and +8.0°C' and heading match must rank first
    assert reranked[0].chunk_id == "chk-002"
    assert reranked[0].rerank_score > reranked[1].rerank_score


def test_noop_reranker_passthrough():
    reranker = NoOpReranker()
    chunks = [
        RankedChunk(
            chunk_id=f"chk-{i}",
            document_id="doc-001",
            document_title="Doc",
            content=f"Content {i}",
        )
        for i in range(5)
    ]

    reranked = reranker.rerank("any query", chunks, top_k=3)
    assert len(reranked) == 3
    assert [c.chunk_id for c in reranked] == ["chk-0", "chk-1", "chk-2"]


def test_query_rewriter_acronym_expansion():
    rewriter = QueryRewriter()
    query = "What is the timeline for RCA and CAPA in a major deviation under SOP?"
    expanded = rewriter.expand_acronyms(query)

    assert "root cause analysis" in expanded
    assert "corrective and preventive action" in expanded
    assert "standard operating procedure" in expanded


def test_query_rewriter_conversational_pronoun_resolution():
    rewriter = QueryRewriter()

    history = [
        MessageContext(role="user", content="What is CLIN-SOP-009 about?"),
        MessageContext(
            role="assistant",
            content="CLIN-SOP-009 covers Refrigerated Storage and Cold Chain Integrity.",
        ),
    ]

    # Follow-up with elliptical pronoun 'its'
    followup = "What are its temperature specifications?"
    rewritten = rewriter.rewrite_query(followup, conversation_history=history)

    assert "CLIN-SOP-009" in rewritten or "Refrigerated Storage" in rewritten
    assert "temperature specifications" in rewritten
