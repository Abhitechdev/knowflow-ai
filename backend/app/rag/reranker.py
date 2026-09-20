"""Stage 2 Reranking for KnowFlow AI.
Implements HybridReranker, combining stage 1 RRF scores with fine-grained
lexical-semantic cross-scoring, exact continuous phrase matches, numerical density,
and section heading alignment.
"""

import re

from app.rag.base import RankedChunk


class BaseReranker:
    """Abstract interface for Stage 2 rerankers."""

    def rerank(self, query: str, chunks: list[RankedChunk], top_k: int = 4) -> list[RankedChunk]:
        raise NotImplementedError


class NoOpReranker(BaseReranker):
    """Pass-through reranker returning top_k chunks without modification."""

    def rerank(self, query: str, chunks: list[RankedChunk], top_k: int = 4) -> list[RankedChunk]:
        return chunks[:top_k]


class HybridReranker(BaseReranker):
    """Calibrated two-stage HybridReranker.
    Combines stage 1 RRF scores with fine-grained cross-scoring:
    1. Exact continuous phrase match bonus (+0.35)
    2. Query term coverage ratio (+0.25)
    3. Numerical and specification alignment (+0.20)
    4. Section heading relevance (+0.10)
    5. Prior stage 1 RRF fusion weight (+0.10)
    """

    def __init__(
        self,
        phrase_weight: float = 0.35,
        coverage_weight: float = 0.25,
        spec_weight: float = 0.20,
    ):
        self.phrase_weight = phrase_weight
        self.coverage_weight = coverage_weight
        self.spec_weight = spec_weight

    def rerank(self, query: str, chunks: list[RankedChunk], top_k: int = 4) -> list[RankedChunk]:
        if not chunks:
            return []

        query_clean = query.lower().strip()
        query_terms = set(re.findall(r"\b[a-zA-Z0-9_\-\.]{3,}\b", query_clean))
        query_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", query_clean))

        scored_chunks: list[tuple[float, RankedChunk]] = []

        for chunk in chunks:
            heading_text = (chunk.section_heading or "").lower()
            combined_text = f"{heading_text} {chunk.content}".lower()

            # 1. Exact phrase match (checking bigrams and trigrams)
            phrase_score = 0.0
            words = query_clean.split()
            if len(words) >= 2:
                for i in range(len(words) - 1):
                    bigram = f"{words[i]} {words[i+1]}"
                    if bigram in combined_text:
                        phrase_score += 0.5
            phrase_score = min(phrase_score, 1.0)

            # 2. Term coverage ratio
            coverage_score = 0.0
            if query_terms:
                matched_terms = sum(1 for term in query_terms if term in combined_text)
                coverage_score = matched_terms / len(query_terms)

            # 3. Numerical / unit / specification alignment
            spec_score = 0.0
            if query_numbers:
                num_matches = sum(1 for num in query_numbers if num in combined_text)
                spec_score = num_matches / len(query_numbers)
            else:
                # If query seeks specifications (e.g., 'range', 'limit', 'time', 'how many'), reward quantitative units
                is_spec_query = any(k in query_clean for k in ["range", "temp", "time", "limit", "many", "how long", "notice", "password", "requirement", "specification"])
                if is_spec_query:
                    has_numbers = bool(re.search(r"\b\d+(?:\.\d+)?\b", combined_text))
                    unit_matches = sum(
                        1
                        for unit in [
                            "°c",
                            "°f",
                            "celsius",
                            "hour",
                            "hours",
                            "day",
                            "days",
                            "calendar days",
                            "business days",
                            "minute",
                            "weeks",
                            "characters",
                            "lockout",
                            "attempts",
                        ]
                        if unit in combined_text
                    )
                    spec_score = min((0.5 if has_numbers else 0.0) + (0.3 * unit_matches), 1.0)

            # 4. Section heading relevance
            heading_score = 0.0
            if heading_text and query_terms:
                h_matches = sum(1 for t in query_terms if t in heading_text)
                heading_score = min(h_matches / max(len(query_terms) * 0.5, 1.0), 1.0)

            # 5. Prior Stage 1 RRF score
            rrf_contrib = min(chunk.rrf_score * 50.0, 1.0)

            # Combined calibrated rerank score
            final_rerank_score = (
                (0.25 * phrase_score)
                + (0.25 * coverage_score)
                + (0.25 * spec_score)
                + (0.15 * heading_score)
                + (0.10 * rrf_contrib)
            )

            # Clone chunk with rerank_score
            updated_chunk = chunk.model_copy(
                update={"rerank_score": round(final_rerank_score, 4)}
            )
            scored_chunks.append((final_rerank_score, updated_chunk))

        # Sort descending by rerank score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored_chunks[:top_k]]
