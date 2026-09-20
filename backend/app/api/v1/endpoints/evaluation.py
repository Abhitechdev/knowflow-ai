"""Evaluation API Endpoints for KnowFlow AI.
Runs automated RAG evaluation benchmark suites and reports retrieval ranking,
faithfulness scores, and False Positive / False Negative counts.
"""

from typing import Optional

from app.auth.context import UserContext, get_current_user_context
from app.db.session import get_db
from app.evaluation.dataset import GOLDEN_BENCHMARK_CASES
from app.evaluation.engine import EvaluationEngine, EvaluationSummary
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

# In-memory cached summary of the most recent evaluation run
_LATEST_EVALUATION_SUMMARY: EvaluationSummary | None = None


@router.post("/run", response_model=EvaluationSummary)
async def run_evaluation_benchmark(
    user_context: UserContext = Depends(get_current_user_context),
    db: AsyncSession = Depends(get_db),
):
    """Triggers an automated evaluation benchmark across the golden test suite.
    Calculates Hit Rate @ 1/3/5, MRR, NDCG@5, Faithfulness, and reports
    False Positives and False Negatives separately.
    """
    global _LATEST_EVALUATION_SUMMARY

    engine = EvaluationEngine(user_context=user_context)
    summary = await engine.run_benchmark(db=db, cases=GOLDEN_BENCHMARK_CASES, top_k=5)
    _LATEST_EVALUATION_SUMMARY = summary
    return summary


@router.get("/summary", response_model=Optional[EvaluationSummary])
async def get_latest_evaluation_summary():
    """Returns the most recent automated evaluation summary."""
    return _LATEST_EVALUATION_SUMMARY
