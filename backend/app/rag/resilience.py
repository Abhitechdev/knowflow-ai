"""Production LLM Resilience Engine for KnowFlow AI.
Enforces:
1. Per-request timeout handling.
2. Exponential backoff retry with jitter on transient failures.
3. Fallback to configured secondary provider (if configured).
4. Circuit breaker protection preventing cascading outages.
5. Safe structured error/refusal under Grounded Answering Policy if all providers fail.
Note: DeterministicLocalLLMProvider is strictly maintained as DEVELOPMENT / TESTING ONLY.
"""

import asyncio
import logging
import random
import time

from app.rag.base import CitationItem, RankedChunk

logger = logging.getLogger(__name__)


class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is tripped open to fail fast."""


class ResilientLLMInvoker:
    """Wraps LLM invocations with retry, secondary provider fallback, and circuit breaker."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay_seconds: float = 0.5,
        timeout_seconds: float = 15.0,
        circuit_breaker_threshold: int = 3,
        circuit_breaker_cooldown: float = 30.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay_seconds
        self.timeout_seconds = timeout_seconds
        self.failure_threshold = circuit_breaker_threshold
        self.cooldown_seconds = circuit_breaker_cooldown

        self.consecutive_failures: int = 0
        self.circuit_open_until: float = 0.0

    def is_circuit_open(self) -> bool:
        """Returns True if the circuit breaker is currently tripped open."""
        now = time.time()
        if self.consecutive_failures >= self.failure_threshold:
            if now < self.circuit_open_until:
                return True
            # Cooldown passed, allow a half-open trial
            self.consecutive_failures = 0
            self.circuit_open_until = 0.0
        return False

    def record_success(self):
        self.consecutive_failures = 0
        self.circuit_open_until = 0.0

    def record_failure(self):
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.circuit_open_until = time.time() + self.cooldown_seconds
            logger.warning(
                f"LLM Circuit Breaker tripped OPEN after {self.consecutive_failures} failures. "
                f"Cooling down for {self.cooldown_seconds}s."
            )

    async def invoke_with_resilience(
        self,
        primary_provider,
        query: str,
        chunks: list[RankedChunk],
        secondary_provider=None,
    ) -> tuple[str, list[CitationItem], int, str]:
        """Executes LLM generation with retry -> secondary provider -> safe structured refusal.
        Returns: (answer_text, citations, tokens_used, provider_status)
        """
        if self.is_circuit_open():
            logger.error("Circuit breaker is OPEN. Failing fast to safe refusal.")
            return (
                ("The AI generation service is temporarily unavailable due to high error rates. "
                "Please retry in a few moments."),
                [],
                0,
                "CIRCUIT_BREAKER_OPEN",
            )

        # Attempt Primary Provider with Retries
        for attempt in range(1, self.max_retries + 1):
            try:
                # Wrap with timeout
                result = await asyncio.wait_for(
                    primary_provider.generate_grounded_answer(query, chunks),
                    timeout=self.timeout_seconds,
                )
                self.record_success()
                answer, citations, tokens = result
                return answer, citations, tokens, "PRIMARY_SUCCESS"

            except Exception as e:
                logger.warning(f"Primary LLM provider attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries:
                    jitter = random.uniform(0.1, 0.3)
                    delay = (self.base_delay * (2 ** (attempt - 1))) + jitter
                    await asyncio.sleep(delay)

        self.record_failure()

        # Attempt Configured Secondary Provider (if provided)
        if secondary_provider:
            logger.info("Attempting configured secondary LLM provider...")
            try:
                result = await asyncio.wait_for(
                    secondary_provider.generate_grounded_answer(query, chunks),
                    timeout=self.timeout_seconds,
                )
                self.record_success()
                answer, citations, tokens = result
                return answer, citations, tokens, "SECONDARY_FALLBACK_SUCCESS"
            except Exception as e:
                logger.error(f"Secondary LLM provider also failed: {e}")

        # All configured providers failed: return safe structured refusal
        safe_refusal = (
            "The verified AI generation service encountered a transient network issue. "
            "To uphold the Grounded Answering Policy, no unverified or speculative claims are generated. "
            "Please try your request again shortly."
        )
        return safe_refusal, [], 0, "FAILED_SAFE_REFUSAL"
