import logging
import re
import time
from abc import ABC, abstractmethod

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import UserContext
from app.core.config import settings
from app.rag.base import (
    CitationItem,
    GroundingAssessment,
    RAGResponse,
    RankedChunk,
)
from app.rag.grounding import POLICY_NAME, GroundingEvaluator
from app.rag.retrieval import HybridRetriever
from app.rag.rewriter import MessageContext, QueryRewriter
from app.security.guardrails import PromptInjectionGuard

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are KnowFlow AI, an enterprise compliance and knowledge assistant.
Your answers are governed by the strict Grounded Answering Policy:
1. Answer ONLY using the factual information contained in the provided Authorized Context chunks below.
2. If the context does not contain enough information to formulate a verified answer, state clearly that the documentation does not provide this information. Never extrapolate, fabricate, or guess.
3. Every factual claim must be backed by citations referencing the source document name, section, and page number.
4. Maintain a professional, structured, and compliant tone.
"""


class BaseLLMProvider(ABC):
    """Abstract interface for LLM synthesis providers."""

    @abstractmethod
    async def generate_grounded_answer(
        self,
        query: str,
        chunks: list[RankedChunk],
    ) -> tuple[str, list[CitationItem], int]:
        """Generates a grounded answer with exact supporting citations and token count."""


class DeterministicLocalLLMProvider(BaseLLMProvider):
    """DEVELOPMENT / TESTING ONLY — NOT FOR PRODUCTION USE.
    Provides deterministic, zero-cost grounded answer synthesis from authorized document chunks
    when running locally without external cloud API credentials.
    """

    PROVIDER_NAME = "DeterministicLocalLLMProvider (DEVELOPMENT / TESTING ONLY)"

    async def generate_grounded_answer(
        self,
        query: str,
        chunks: list[RankedChunk],
    ) -> tuple[str, list[CitationItem], int]:
        if not chunks:
            return (
                f"Under the {POLICY_NAME}, no verified documentation was found to answer: '{query}'.",
                [],
                0,
            )

        # Gather candidate sentences from the retrieved chunks
        candidates = []
        query_words = set(re.findall(r"\b\w{3,}\b", query.lower()))
        time_related_terms = {"time", "limit", "reporting", "sla", "hours", "days", "timeline", "investigation", "closure", "period"}
        temp_related_terms = {"temperature", "range", "degrees", "celsius", "cold", "chain", "stored", "storage"}
        has_time_intent = bool(query_words & time_related_terms)
        has_temp_intent = bool(query_words & temp_related_terms)

        for c in chunks[:3]:
            # Split sentences by punctuation or newlines
            sentences = [s.strip() for s in re.split(r"(?:[.!?]\s+|\n+)", c.content) if len(s.strip()) > 15]
            for s in sentences:
                s_words = set(re.findall(r"\b\w{3,}\b", s.lower()))
                overlap = len(s_words & query_words)
                # Boost if query asked about time/limits and sentence has time keywords or numbers
                if has_time_intent and any(t in s.lower() for t in ["hour", "day", "business day", "sla", "within", "limit", "timeline"]):
                    overlap += 3
                # Substantive temperature specification boost (requires actual numbers or units)
                if has_temp_intent and any(t in s.lower() for t in ["°c", "°f", "celsius", "fahrenheit", "+2", "+8", "2.0", "8.0", "-20", "-80"]):
                    overlap += 8
                elif has_temp_intent and any(t in s.lower() for t in ["refrigerated", "storage", "ambient", "iot"]):
                    overlap += 2
                if overlap > 0:
                    candidates.append((overlap, c, s))

        if candidates:
            # Sort by keyword overlap descending
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_chunk = candidates[0][1]
            # Take top 2-3 matched sentences from that chunk
            chunk_matched = [c[2] for c in candidates if c[1] == best_chunk][:3]
            supporting_excerpt = " ".join(chunk_matched)
            top_chunk = best_chunk
        else:
            top_chunk = chunks[0]
            sentences = [s.strip() for s in re.split(r"(?:[.!?]\s+|\n+)", top_chunk.content) if len(s.strip()) > 15]
            supporting_excerpt = " ".join(sentences[:3]) if sentences else top_chunk.content[:200]

        # Synthesize clear, verified answer citing the exact source and excerpt
        answer = (
            f"Based on verified company documentation from **{top_chunk.document_title}** "
            f"(Section: *{top_chunk.section_heading}*, Page {top_chunk.page_number}):\n\n"
            f"{supporting_excerpt}\n\n"
            f"> *Verified via {POLICY_NAME}. Ref: [{top_chunk.document_title} - P.{top_chunk.page_number}]*"
        )

        citations: list[CitationItem] = []
        for c in chunks[:3]:
            # Find evidence excerpt for each citation that best supports the query
            c_sentences = [s.strip() for s in re.split(r"(?:[.!?]\s+|\n+)", c.content) if len(s.strip()) > 15]
            best_s = None
            best_score = -1
            for s in c_sentences:
                s_words = set(re.findall(r"\b\w{3,}\b", s.lower()))
                score = len(s_words & query_words)
                if has_time_intent and any(t in s.lower() for t in ["hour", "day", "business day", "sla", "within", "limit", "timeline"]):
                    score += 2
                if has_temp_intent and any(t in s.lower() for t in ["°c", "°f", "celsius", "fahrenheit", "+2", "+8", "2.0", "8.0", "temperature", "cold", "storage", "temp", "quarantine", "excursion"]):
                    score += 2
                if score > best_score:
                    best_score = score
                    best_s = s
            c_excerpt = best_s if (best_s and best_score > 0) else (" ".join(c_sentences[:2]) if c_sentences else c.content[:200])
            citations.append(
                CitationItem(
                    document_id=c.document_id,
                    chunk_id=c.chunk_id,
                    document_title=c.document_title,
                    page_number=c.page_number,
                    section_heading=c.section_heading,
                    relevant_text=c_excerpt,
                    confidence=round(max(c.dense_score, c.sparse_score, 0.5), 3),
                )
            )

        estimated_tokens = len(answer.split()) + sum(len(c.content.split()) for c in chunks[:3])
        return answer, citations, estimated_tokens


class OpenAILLMProvider(BaseLLMProvider):
    """Production LLM provider using OpenAI API or OpenAI-compatible gateway."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    async def generate_grounded_answer(
        self,
        query: str,
        chunks: list[RankedChunk],
    ) -> tuple[str, list[CitationItem], int]:
        context_parts = []
        for i, c in enumerate(chunks, 1):
            context_parts.append(
                f"[Chunk {i}] Document: '{c.document_title}' | Section: '{c.section_heading}' | Page: {c.page_number}\n{c.content}"
            )
        context_text = "\n\n---\n\n".join(context_parts)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Authorized Context Chunks:\n\n{context_text}\n\nQuestion: {query}",
            },
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.0,  # Zero temperature for maximum factual consistency
                },
            )
            res.raise_for_status()
            data = res.json()
            answer = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)

        # Build citations from top chunks
        citations = []
        for c in chunks[:3]:
            citations.append(
                CitationItem(
                    document_id=c.document_id,
                    chunk_id=c.chunk_id,
                    document_title=c.document_title,
                    page_number=c.page_number,
                    section_heading=c.section_heading,
                    relevant_text=c.content[:250],
                    confidence=round(max(c.dense_score, c.sparse_score, 0.7), 3),
                )
            )

        return answer, citations, tokens_used


class GeminiLLMProvider(BaseLLMProvider):
    """Production LLM provider using Google Gemini API."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        # Strip models/ prefix if present
        self.model_name = model_name.replace("models/", "") if model_name else "gemini-1.5-flash"

    async def generate_grounded_answer(
        self,
        query: str,
        chunks: list[RankedChunk],
    ) -> tuple[str, list[CitationItem], int]:
        context_parts = []
        for i, c in enumerate(chunks, 1):
            context_parts.append(
                f"[Chunk {i}] Document: '{c.document_title}' | Section: '{c.section_heading}' | Page: {c.page_number}\n{c.content}"
            )
        context_text = "\n\n---\n\n".join(context_parts)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"Authorized Context Chunks:\n\n{context_text}\n\nQuestion: {query}"}
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            res.raise_for_status()
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                answer = parts[0].get("text", "") if parts else ""
            else:
                answer = "No response generated by the model."
            tokens_used = data.get("usageMetadata", {}).get("totalTokenCount", 0)

        # Build citations from top chunks
        citations = []
        for c in chunks[:3]:
            citations.append(
                CitationItem(
                    document_id=c.document_id,
                    chunk_id=c.chunk_id,
                    document_title=c.document_title,
                    page_number=c.page_number,
                    section_heading=c.section_heading,
                    relevant_text=c.content[:250],
                    confidence=round(max(c.dense_score, c.sparse_score, 0.7), 3),
                )
            )

        return answer, citations, tokens_used


def get_llm_provider() -> BaseLLMProvider:
    """Returns the configured LLM provider, defaulting safely to DeterministicLocalLLMProvider
    for development and automated testing environments.
    """
    gemini_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY or (settings.LLM_API_KEY if settings.LLM_PROVIDER.lower() in ("gemini", "google") else "")
    if (settings.LLM_PROVIDER.lower() in ("gemini", "google") and gemini_key) or (gemini_key and settings.LLM_PROVIDER.lower() != "openai"):
        try:
            model = settings.LLM_MODEL if "gemini" in (settings.LLM_MODEL or "").lower() else "gemini-1.5-flash"
            return GeminiLLMProvider(api_key=gemini_key, model_name=model)
        except Exception as e:
            logger.warning(f"Failed to initialize GeminiLLMProvider: {e}. Falling back to local deterministic provider.")

    if settings.LLM_PROVIDER == "openai" and settings.LLM_API_KEY:
        try:
            return OpenAILLMProvider(
                api_key=settings.LLM_API_KEY,
                model_name=settings.LLM_MODEL or "gpt-4o-mini",
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAILLMProvider: {e}. Falling back to local deterministic provider.")

    return DeterministicLocalLLMProvider()


class RAGService:
    """Full-cycle RAG coordinator enforcing:
    1. Server-side authorization and workspace isolation.
    2. Hybrid dense + sparse retrieval with RRF.
    3. Grounded Answering Policy (honesty over hallucination).
    4. Exact citation and evidence mapping.
    """

    def __init__(self):
        self.retriever = HybridRetriever(top_k=4)
        self.evaluator = GroundingEvaluator()
        self.rewriter = QueryRewriter()
        self.guard = PromptInjectionGuard()

    async def answer_query(
        self,
        query: str,
        user_context: UserContext,
        db: AsyncSession,
        department_filter: str | None = None,
        conversation_history: list[MessageContext] | None = None,
    ) -> RAGResponse:
        start_time = time.perf_counter()

        # Step -1: Security & Prompt Injection Inspection
        injection_res = self.guard.inspect_query(query)
        if not injection_res.is_safe:
            logger.warning(
                f"Prompt injection pattern detected from user {user_context.user_id}: {injection_res.flagged_patterns}"
            )
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            assessment = GroundingAssessment(
                is_sufficient=False,
                confidence_score=0.0,
                reason="Prohibited instruction override or jailbreak pattern detected.",
                policy=POLICY_NAME,
            )
            return RAGResponse(
                answer=(
                    f"Under KnowFlow's **{POLICY_NAME}**, input containing system instruction overrides, "
                    f"jailbreak patterns, or delimiter injection is blocked. Please rephrase your query "
                    f"as a standard inquiry regarding company policies or SOPs."
                ),
                is_grounded=False,
                grounding_status="BLOCKED_SECURITY_INJECTION",
                policy_applied=POLICY_NAME,
                citations=[],
                model_used="PromptInjectionGuard:Blocked",
                latency_ms=latency_ms,
                tokens_used=0,
                grounding_assessment=assessment,
            )

        # Step 0: Query Disambiguation & Terminology Expansion
        sanitized_query = injection_res.sanitized_text
        effective_query = self.rewriter.rewrite_query(sanitized_query, conversation_history=conversation_history)

        # Step 1: Hybrid Retrieval with Stage 2 Reranker enforcing server-side authorization
        retrieval_res = await self.retriever.retrieve(
            query=effective_query,
            user_context=user_context,
            db=db,
            department_filter=department_filter,
        )

        # Step 2: Evidence Sufficiency Evaluation (Grounded Answering Policy)
        assessment = self.evaluator.evaluate(sanitized_query, retrieval_res.chunks)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # If evidence is insufficient, enforce refusal under Grounded Answering Policy
        if not assessment.is_sufficient:
            refusal_text = self.evaluator.generate_refusal_answer(query, assessment)
            return RAGResponse(
                answer=refusal_text,
                is_grounded=False,
                grounding_status="REFUSED_INSUFFICIENT_EVIDENCE",
                policy_applied=POLICY_NAME,
                citations=[],
                model_used="GroundingEvaluator:Refusal",
                latency_ms=latency_ms,
                tokens_used=0,
                grounding_assessment=assessment,
            )

        # Step 3: LLM Generation from verified evidence
        llm = get_llm_provider()
        model_name = (
            getattr(llm, "PROVIDER_NAME", None)
            or getattr(llm, "model_name", None)
            or llm.__class__.__name__
        )

        answer_text, citations, tokens = await llm.generate_grounded_answer(
            query=query,
            chunks=retrieval_res.chunks,
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return RAGResponse(
            answer=answer_text,
            is_grounded=True,
            grounding_status="VERIFIED",
            policy_applied=POLICY_NAME,
            citations=citations,
            model_used=model_name,
            latency_ms=latency_ms,
            tokens_used=tokens,
            grounding_assessment=assessment,
        )
