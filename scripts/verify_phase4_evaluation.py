"""Verification script for Phase 4 Automated RAG Evaluation Benchmark.
Executes the golden benchmark dataset and outputs detailed ranking, faithfulness,
and false positive/negative statistics.
"""

import asyncio
from app.db.session import get_session_factory
from app.evaluation.dataset import GOLDEN_BENCHMARK_CASES
from app.evaluation.engine import EvaluationEngine


async def main():
    print("=" * 60)
    print("PHASE 4: AUTOMATED RAG EVALUATION BENCHMARK RUNNER")
    print("=" * 60)

    session_factory = get_session_factory()
    if session_factory is None:
        print("Database session factory unavailable. Check DATABASE_URL.")
        return

    async with session_factory() as db:
        engine = EvaluationEngine()
        print(f"Executing {len(GOLDEN_BENCHMARK_CASES)} benchmark cases...")
        summary = await engine.run_benchmark(db=db, cases=GOLDEN_BENCHMARK_CASES, top_k=5)

        print("\n--- RETRIEVAL & RANKING METRICS ---")
        print(f"Hit Rate @ 1 : {summary.hit_rate_at_1 * 100:.1f}%")
        print(f"Hit Rate @ 3 : {summary.hit_rate_at_3 * 100:.1f}%")
        print(f"Hit Rate @ 5 : {summary.hit_rate_at_5 * 100:.1f}%")
        print(f"MRR          : {summary.mrr:.4f}")
        print(f"NDCG @ 5     : {summary.ndcg_at_5:.4f}")

        print("\n--- FAITHFULNESS & GROUNDED ANSWERING POLICY ---")
        print(f"Avg Faithfulness Score : {summary.avg_faithfulness * 100:.1f}%")
        print(f"Refusal Accuracy       : {summary.refusal_accuracy_pct:.1f}%")
        print(f"False Positives (In-scope refused) : {summary.false_positives}")
        print(f"False Negatives (Out-of-scope answered): {summary.false_negatives}")

        print("\n--- BENCHMARK PASS / FAIL OVERVIEW ---")
        print(f"Total Cases  : {summary.total_cases}")
        print(f"In-Scope     : {summary.in_scope_cases}")
        print(f"Out-of-Scope : {summary.out_of_scope_cases}")
        print(f"Passed Cases : {summary.passed_cases}")
        print(f"Failed Cases : {summary.failed_cases}")
        print(f"Pass Rate    : {summary.pass_rate_pct:.1f}%")
        print(f"Avg Latency  : {summary.avg_latency_ms:.1f}ms")

        print("\n--- PER-CASE BREAKDOWN ---")
        for c in summary.case_results:
            status = "PASS" if c.passed else "FAIL"
            out_flag = "[OUT-OF-SCOPE]" if c.is_out_of_scope else "[IN-SCOPE]"
            print(f"[{status}] {c.case_id} {out_flag} - '{c.question[:45]}...' (Faith: {c.faithfulness_score:.2f}, Latency: {c.latency_ms}ms)")

        print("=" * 60)
        return summary


if __name__ == "__main__":
    asyncio.run(main())
