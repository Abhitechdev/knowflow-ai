"""Answer Groundedness & Faithfulness Evaluation.
Measures sentence-level factual support against cited context excerpts and tracks
False Positives (in-scope refused) and False Negatives (out-of-scope answered).
"""

import re
from collections.abc import Sequence

from pydantic import BaseModel


class SentenceVerification(BaseModel):
    sentence: str
    is_supported: bool
    matching_keywords: list[str]
    overlap_ratio: float


class FaithfulnessResult(BaseModel):
    is_faithful: bool
    faithfulness_score: float  # Supported sentences / total sentences
    supported_sentences: int
    total_sentences: int
    sentence_verifications: list[SentenceVerification]
    is_refusal: bool
    is_false_positive: bool  # Valid in-scope question erroneously refused
    is_false_negative: bool  # Out-of-scope question answered without refusal


def split_sentences(text: str) -> list[str]:
    """Splits response text into clean, non-trivial claim statements,
    avoiding false splits on decimal points or section numbers.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    clean = []
    for l in lines:
        if l.lower().startswith("based on verified") or l.startswith(">"):
            continue
        sub_sentences = re.split(r"(?<=[a-zA-Z]{2}[.!?])\s+(?=[A-Z])", l)
        for s in sub_sentences:
            s_clean = re.sub(r"[\*\-_#]", " ", s).strip()
            s_clean = re.sub(r"\s+", " ", s_clean)
            if len(s_clean) > 15:
                clean.append(s_clean)
    return clean


def evaluate_faithfulness(
    answer: str,
    context_excerpts: Sequence[str],
    is_out_of_scope: bool,
    is_grounded: bool,
    grounding_status: str,
) -> FaithfulnessResult:
    """Evaluates whether generated answer claims are supported by context excerpts.
    Reports False Positives and False Negatives separately.
    """
    is_refusal = not is_grounded or "REFUSED" in grounding_status.upper()

    # Track classification errors
    is_false_negative = False

    if is_out_of_scope:
        if not is_refusal:
            # Out-of-scope question was answered: FALSE NEGATIVE (harmful hallucination)
            is_false_negative = True
        return FaithfulnessResult(
            is_faithful=not is_false_negative,
            faithfulness_score=0.0 if is_false_negative else 1.0,
            supported_sentences=0,
            total_sentences=0,
            sentence_verifications=[],
            is_refusal=is_refusal,
            is_false_positive=False,
            is_false_negative=is_false_negative,
        )

    # In-scope question
    if is_refusal:
        # In-scope question was erroneously refused: FALSE POSITIVE
        return FaithfulnessResult(
            is_faithful=False,
            faithfulness_score=0.0,
            supported_sentences=0,
            total_sentences=0,
            sentence_verifications=[],
            is_refusal=True,
            is_false_positive=True,
            is_false_negative=False,
        )

    sentences = split_sentences(answer)
    if not sentences:
        return FaithfulnessResult(
            is_faithful=True,
            faithfulness_score=1.0,
            supported_sentences=0,
            total_sentences=0,
            sentence_verifications=[],
            is_refusal=False,
            is_false_positive=False,
            is_false_negative=False,
        )

    combined_context = " ".join(context_excerpts).lower()
    context_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-\.]{3,}\b", combined_context))

    verifications: list[SentenceVerification] = []
    supported_count = 0

    for sentence in sentences:
        s_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-\.]{3,}\b", sentence.lower()))
        if not s_tokens:
            continue

        overlap = s_tokens.intersection(context_tokens)
        overlap_ratio = len(overlap) / len(s_tokens) if s_tokens else 0.0

        # A sentence is supported if a substantial portion of its key terms exist in the retrieved context
        is_supported = overlap_ratio >= 0.40 or len(overlap) >= 3
        if is_supported:
            supported_count += 1

        verifications.append(
            SentenceVerification(
                sentence=sentence,
                is_supported=is_supported,
                matching_keywords=list(overlap)[:8],
                overlap_ratio=round(overlap_ratio, 3),
            )
        )

    score = supported_count / len(verifications) if verifications else 1.0
    is_faithful = score >= 0.75

    return FaithfulnessResult(
        is_faithful=is_faithful,
        faithfulness_score=round(score, 3),
        supported_sentences=supported_count,
        total_sentences=len(verifications),
        sentence_verifications=verifications,
        is_refusal=False,
        is_false_positive=False,
        is_false_negative=False,
    )
