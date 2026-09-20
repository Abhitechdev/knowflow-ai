"""Automated RAG Evaluation Benchmark Engine.
Executes benchmark datasets, measures retrieval precision/recall, MRR, NDCG,
answer faithfulness, and reports False Positives & False Negatives separately.
"""

import time

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import UserContext
from app.evaluation.dataset import GOLDEN_BENCHMARK_CASES, BenchmarkCase
from app.evaluation.faithfulness import evaluate_faithfulness
from app.evaluation.metrics import (
    calculate_hit_rate,
    calculate_mrr,
    calculate_ndcg_at_k,
)
from app.rag.llm import RAGService


class CaseEvaluationResult(BaseModel):
    case_id: str
    question: str
    category: str
    is_out_of_scope: bool
    retrieved_doc_titles: list[str]
    retrieved_sections: list[str]
    hit_at_1: float
    hit_at_3: float
    hit_at_5: float
    mrr: float
    ndcg_at_5: float
    is_grounded: bool
    grounding_status: str
    faithfulness_score: float
    is_faithful: bool
    is_false_positive: bool
    is_false_negative: bool
    latency_ms: float
    passed: bool


class EvaluationSummary(BaseModel):
    total_cases: int
    in_scope_cases: int
    out_of_scope_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate_pct: float
    hit_rate_at_1: float
    hit_rate_at_3: float
    hit_rate_at_5: float
    mrr: float
    ndcg_at_5: float
    avg_faithfulness: float
    false_positives: int  # In-scope refused
    false_negatives: int  # Out-of-scope answered
    refusal_accuracy_pct: float
    avg_latency_ms: float
    case_results: list[CaseEvaluationResult]


class EvaluationEngine:
    """Automated benchmark executor for KnowFlow AI RAG."""

    def __init__(self, user_context: UserContext | None = None):
        self.user_context = user_context or UserContext(
            user_id="usr-eval-admin",
            workspace_id="ws-default-001",
            role="ADMIN",
            department_id="QUALITY",
            email="eval-admin@knowflow.internal",
            is_admin=True,
        )
        self.rag_service = RAGService()

    async def run_benchmark(
        self, db: AsyncSession, cases: list[BenchmarkCase] | None = None, top_k: int = 5
    ) -> EvaluationSummary:
        """Executes all benchmark cases and returns a comprehensive quantitative evaluation summary."""
        test_cases = cases or GOLDEN_BENCHMARK_CASES
        case_results: list[CaseEvaluationResult] = []

        total_hit_1 = 0.0
        total_hit_3 = 0.0
        total_hit_5 = 0.0
        total_mrr = 0.0
        total_ndcg = 0.0
        total_faithfulness = 0.0
        total_latency = 0.0
        false_positives = 0
        false_negatives = 0
        in_scope_count = 0
        out_of_scope_count = 0

        for case in test_cases:
            t_start = time.perf_counter()

            # Execute RAG query
            rag_response = await self.rag_service.answer_query(
                query=case.question,
                user_context=self.user_context,
                db=db,
            )
            t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            total_latency += t_elapsed_ms

            # Collect retrieved document titles
            retrieved_doc_titles = [c.document_title for c in rag_response.citations]
            retrieved_sections = [c.section_heading for c in rag_response.citations]
            context_excerpts = [
                f"{c.document_title} {c.section_heading} {c.relevant_text}"
                for c in rag_response.citations
            ]

            if case.is_out_of_scope:
                out_of_scope_count += 1
                hit_1 = 0.0
                hit_3 = 0.0
                hit_5 = 0.0
                mrr = 0.0
                ndcg = 0.0
            else:
                in_scope_count += 1
                hit_1 = calculate_hit_rate(retrieved_doc_titles, case.expected_doc_title or "", k=1)
                hit_3 = calculate_hit_rate(retrieved_doc_titles, case.expected_doc_title or "", k=3)
                hit_5 = calculate_hit_rate(retrieved_doc_titles, case.expected_doc_title or "", k=5)
                mrr = calculate_mrr(retrieved_doc_titles, case.expected_doc_title or "")
                expected_list = [case.expected_doc_title] if case.expected_doc_title else []
                ndcg = calculate_ndcg_at_k(retrieved_doc_titles, expected_list, k=5)

                total_hit_1 += hit_1
                total_hit_3 += hit_3
                total_hit_5 += hit_5
                total_mrr += mrr
                total_ndcg += ndcg

            # Evaluate faithfulness & refusal behavior
            faith_result = evaluate_faithfulness(
                answer=rag_response.answer,
                context_excerpts=context_excerpts,
                is_out_of_scope=case.is_out_of_scope,
                is_grounded=rag_response.is_grounded,
                grounding_status=rag_response.grounding_status,
            )

            if faith_result.is_false_positive:
                false_positives += 1
            if faith_result.is_false_negative:
                false_negatives += 1

            if not case.is_out_of_scope:
                total_faithfulness += faith_result.faithfulness_score

            # Case is considered passed if:
            # - For out-of-scope: correctly refused (not false negative)
            # - For in-scope: retrieved target document (hit@5) AND faithful (not false positive)
            if case.is_out_of_scope:
                passed = not faith_result.is_false_negative and faith_result.is_refusal
            else:
                passed = hit_5 > 0.0 and faith_result.is_faithful and not faith_result.is_false_positive

            case_results.append(
                CaseEvaluationResult(
                    case_id=case.id,
                    question=case.question,
                    category=case.category,
                    is_out_of_scope=case.is_out_of_scope,
                    retrieved_doc_titles=retrieved_doc_titles,
                    retrieved_sections=retrieved_sections,
                    hit_at_1=hit_1,
                    hit_at_3=hit_3,
                    hit_at_5=hit_5,
                    mrr=round(mrr, 4),
                    ndcg_at_5=round(ndcg, 4),
                    is_grounded=rag_response.is_grounded,
                    grounding_status=rag_response.grounding_status,
                    faithfulness_score=faith_result.faithfulness_score,
                    is_faithful=faith_result.is_faithful,
                    is_false_positive=faith_result.is_false_positive,
                    is_false_negative=faith_result.is_false_negative,
                    latency_ms=round(t_elapsed_ms, 2),
                    passed=passed,
                )
            )

        total_cases = len(test_cases)
        passed_count = sum(1 for c in case_results if c.passed)
        refusal_total = out_of_scope_count
        refusal_correct = refusal_total - false_negatives

        return EvaluationSummary(
            total_cases=total_cases,
            in_scope_cases=in_scope_count,
            out_of_scope_cases=out_of_scope_count,
            passed_cases=passed_count,
            failed_cases=total_cases - passed_count,
            pass_rate_pct=round((passed_count / total_cases) * 100.0, 2) if total_cases else 0.0,
            hit_rate_at_1=round(total_hit_1 / in_scope_count, 4) if in_scope_count else 0.0,
            hit_rate_at_3=round(total_hit_3 / in_scope_count, 4) if in_scope_count else 0.0,
            hit_rate_at_5=round(total_hit_5 / in_scope_count, 4) if in_scope_count else 0.0,
            mrr=round(total_mrr / in_scope_count, 4) if in_scope_count else 0.0,
            ndcg_at_5=round(total_ndcg / in_scope_count, 4) if in_scope_count else 0.0,
            avg_faithfulness=round(total_faithfulness / in_scope_count, 4) if in_scope_count else 0.0,
            false_positives=false_positives,
            false_negatives=false_negatives,
            refusal_accuracy_pct=round((refusal_correct / refusal_total) * 100.0, 2) if refusal_total else 100.0,
            avg_latency_ms=round(total_latency / total_cases, 2) if total_cases else 0.0,
            case_results=case_results,
        )
