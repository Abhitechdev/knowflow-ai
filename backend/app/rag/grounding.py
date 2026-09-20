import logging

from app.rag.base import GroundingAssessment, RankedChunk

logger = logging.getLogger(__name__)

POLICY_NAME = "Grounded Answering Policy"

# Sufficiency thresholds calibrated for 384-dim embeddings + BM25
MIN_DENSE_THRESHOLD = 0.55
MIN_SPARSE_THRESHOLD = 0.20


class GroundingEvaluator:
    """Enforces the Grounded Answering Policy.
    The system must answer strictly from retrieved, verified company documentation
    and refuse when sufficient evidence is unavailable.
    """

    def evaluate(self, query: str, chunks: list[RankedChunk]) -> GroundingAssessment:
        """Determines whether the retrieved chunks provide sufficient, credible evidence
        to answer the user's question without guessing or hallucinating.
        """
        if not chunks:
            return GroundingAssessment(
                is_sufficient=False,
                confidence_score=0.0,
                reason="No matching company documents found within authorized access scope.",
                policy=POLICY_NAME,
            )

        top_chunk = chunks[0]
        max_dense = max((c.dense_score for c in chunks), default=0.0)
        max_sparse = max((c.sparse_score for c in chunks), default=0.0)
        max_rrf = max((c.rrf_score for c in chunks), default=0.0)

        # Grounding condition:
        # 1. If no keywords match at all (max_sparse == 0), require high dense similarity (>= 0.65)
        # 2. Otherwise require either solid dense match + keyword match, or strong keyword match (>= 0.35), or strong dense (>= 0.60)
        if max_sparse <= 0.001:
            is_sufficient = max_dense >= 0.65
        else:
            is_sufficient = (
                (max_dense >= MIN_DENSE_THRESHOLD and max_sparse >= MIN_SPARSE_THRESHOLD)
                or (max_dense >= 0.60)
                or (max_sparse >= 0.35)
            )

        if is_sufficient:
            confidence = min(1.0, max(max_dense, max_sparse * 1.1, max_rrf * 35.0))
            return GroundingAssessment(
                is_sufficient=True,
                confidence_score=round(confidence, 3),
                reason=f"Verified evidence identified across {len(chunks)} authorized chunk(s) (Top document: {top_chunk.document_title}).",
                policy=POLICY_NAME,
            )

        return GroundingAssessment(
            is_sufficient=False,
            confidence_score=round(max(max_dense, max_sparse), 3),
            reason=(
                f"Retrieved content lacks sufficient evidence to formulate a verified answer "
                f"(Max similarity: {max(max_dense, max_sparse):.2f} < threshold). "
                f"Refusal enforced under {POLICY_NAME}."
            ),
            policy=POLICY_NAME,
        )

    def generate_refusal_answer(self, query: str, assessment: GroundingAssessment) -> str:
        """Standard refusal response adhering strictly to the Grounded Answering Policy."""
        return (
            f"Under KnowFlow's **{POLICY_NAME}**, I can only provide answers verified by "
            f"authorized company documentation and Standard Operating Procedures.\n\n"
            f"I reviewed the internal knowledge base for your inquiry regarding *\"{query}\"*, "
            f"but no verified procedures or manuals contained sufficient evidence to answer this question. "
            f"To prevent inaccuracies, no ungrounded claims or assumptions are made.\n\n"
            f"**Recommendation**: Please check if the relevant SOP, policy, or manual has been uploaded to your workspace, "
            f"or consult your department compliance lead."
        )
