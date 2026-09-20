"""Token Budgeting, Context Window Optimization & Latency Telemetry.
Manages prompt token budgets with sentence-aware chunk truncation,
deduplication, and fine-grained latency timing spans.
"""

import re

from pydantic import BaseModel

from app.rag.base import RankedChunk


class PipelineTimings(BaseModel):
    t_embed_ms: float = 0.0
    t_dense_ms: float = 0.0
    t_sparse_ms: float = 0.0
    t_rerank_ms: float = 0.0
    t_grounding_ms: float = 0.0
    t_llm_ms: float = 0.0
    t_total_ms: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "t_embed_ms": round(self.t_embed_ms, 2),
            "t_dense_ms": round(self.t_dense_ms, 2),
            "t_sparse_ms": round(self.t_sparse_ms, 2),
            "t_rerank_ms": round(self.t_rerank_ms, 2),
            "t_grounding_ms": round(self.t_grounding_ms, 2),
            "t_llm_ms": round(self.t_llm_ms, 2),
            "t_total_ms": round(self.t_total_ms, 2),
        }


class ContextBudgetManager:
    """Budgets context window tokens and cleanly truncates at sentence boundaries."""

    def __init__(self, max_context_tokens: int = 3500):
        self.max_context_tokens = max_context_tokens

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic token estimation (~4 chars per token)."""
        return max(1, len(text) // 4)

    def optimize_chunks(self, chunks: list[RankedChunk]) -> list[RankedChunk]:
        """Deduplicates overlapping content and trims chunks to fit within the token budget."""
        if not chunks:
            return []

        optimized: list[RankedChunk] = []
        seen_sentences = set()
        accumulated_tokens = 0

        for chunk in chunks:
            # Split into sentences
            sentences = re.split(r"(?<=[.!?])\s+", chunk.content)
            unique_sentences = []

            for s in sentences:
                s_norm = s.strip().lower()
                if len(s_norm) > 20 and s_norm in seen_sentences:
                    continue  # Deduplicate repeated boilerplate sentences
                seen_sentences.add(s_norm)
                unique_sentences.append(s.strip())

            trimmed_content = " ".join(unique_sentences)
            chunk_tokens = self.estimate_tokens(trimmed_content)

            if accumulated_tokens + chunk_tokens <= self.max_context_tokens:
                optimized.append(
                    chunk.model_copy(update={"content": trimmed_content})
                )
                accumulated_tokens += chunk_tokens
            else:
                # Truncate at sentence boundary to fit remaining budget
                remaining_tokens = self.max_context_tokens - accumulated_tokens
                if remaining_tokens > 50:
                    budget_chars = remaining_tokens * 4
                    truncated_sentences = []
                    char_count = 0
                    for s in unique_sentences:
                        if char_count + len(s) <= budget_chars:
                            truncated_sentences.append(s)
                            char_count += len(s) + 1
                        else:
                            break
                    if truncated_sentences:
                        optimized.append(
                            chunk.model_copy(update={"content": " ".join(truncated_sentences)})
                        )
                break  # Budget exhausted

        return optimized if optimized else chunks[:1]
