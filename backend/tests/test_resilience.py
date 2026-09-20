"""Unit tests for Phase 4 LLM Resilience: Retry, Secondary Provider Fallback & Circuit Breaker."""

import asyncio
import pytest
from app.rag.base import CitationItem, RankedChunk
from app.rag.resilience import ResilientLLMInvoker


class MockFailingProvider:
    def __init__(self, fail_count: int = 1):
        self.attempts = 0
        self.fail_count = fail_count

    async def generate_grounded_answer(self, query: str, chunks):
        self.attempts += 1
        if self.attempts <= self.fail_count:
            raise ConnectionError("Simulated network timeout/failure")
        return "Recovered answer from primary.", [CitationItem(document_id="d1", document_title="Doc", page_number=1, section_heading="Sec", relevant_text="Excerpt")], 150


class MockPermanentFailProvider:
    async def generate_grounded_answer(self, query: str, chunks):
        raise RuntimeError("Permanent API outage 503")


class MockSuccessfulProvider:
    async def generate_grounded_answer(self, query: str, chunks):
        return "Answer from secondary fallback.", [], 100


@pytest.mark.asyncio
async def test_retry_on_transient_failure():
    invoker = ResilientLLMInvoker(max_retries=3, base_delay_seconds=0.01, timeout_seconds=2.0)
    provider = MockFailingProvider(fail_count=2)

    answer, citations, tokens, status = await invoker.invoke_with_resilience(
        primary_provider=provider,
        query="Test query",
        chunks=[],
    )

    assert status == "PRIMARY_SUCCESS"
    assert "Recovered answer" in answer
    assert provider.attempts == 3


@pytest.mark.asyncio
async def test_fallback_to_secondary_provider():
    invoker = ResilientLLMInvoker(max_retries=2, base_delay_seconds=0.01, timeout_seconds=2.0)
    primary = MockPermanentFailProvider()
    secondary = MockSuccessfulProvider()

    answer, citations, tokens, status = await invoker.invoke_with_resilience(
        primary_provider=primary,
        query="Test query",
        chunks=[],
        secondary_provider=secondary,
    )

    assert status == "SECONDARY_FALLBACK_SUCCESS"
    assert "secondary fallback" in answer


@pytest.mark.asyncio
async def test_safe_structured_refusal_when_all_fail():
    invoker = ResilientLLMInvoker(max_retries=2, base_delay_seconds=0.01, timeout_seconds=2.0)
    primary = MockPermanentFailProvider()
    secondary = MockPermanentFailProvider()

    answer, citations, tokens, status = await invoker.invoke_with_resilience(
        primary_provider=primary,
        query="Test query",
        chunks=[],
        secondary_provider=secondary,
    )

    assert status == "FAILED_SAFE_REFUSAL"
    assert "Grounded Answering Policy" in answer
    assert citations == []


@pytest.mark.asyncio
async def test_circuit_breaker_trips_open():
    invoker = ResilientLLMInvoker(
        max_retries=1,
        base_delay_seconds=0.01,
        timeout_seconds=2.0,
        circuit_breaker_threshold=2,
        circuit_breaker_cooldown=10.0,
    )
    primary = MockPermanentFailProvider()

    # Fail 1
    await invoker.invoke_with_resilience(primary, "q1", [])
    assert invoker.is_circuit_open() is False

    # Fail 2 (trips threshold)
    await invoker.invoke_with_resilience(primary, "q2", [])
    assert invoker.is_circuit_open() is True

    # Immediate next attempt fails fast with CIRCUIT_BREAKER_OPEN
    ans, cits, toks, status = await invoker.invoke_with_resilience(primary, "q3", [])
    assert status == "CIRCUIT_BREAKER_OPEN"
