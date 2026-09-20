"""KnowFlow AI Evaluation Engine.
Provides automated benchmark execution, retrieval ranking metrics, and answer faithfulness scoring.
"""

from app.evaluation.dataset import GOLDEN_BENCHMARK_CASES, BenchmarkCase
from app.evaluation.engine import (
    CaseEvaluationResult,
    EvaluationEngine,
    EvaluationSummary,
)
from app.evaluation.faithfulness import evaluate_faithfulness
from app.evaluation.metrics import (
    calculate_hit_rate,
    calculate_mrr,
    calculate_ndcg_at_k,
    calculate_precision_at_k,
    calculate_recall_at_k,
)

__all__ = [
    "GOLDEN_BENCHMARK_CASES",
    "BenchmarkCase",
    "EvaluationEngine",
    "EvaluationResult",
    "EvaluationSummary",
    "calculate_hit_rate",
    "calculate_mrr",
    "calculate_ndcg_at_k",
    "calculate_precision_at_k",
    "calculate_recall_at_k",
    "evaluate_faithfulness",
]
