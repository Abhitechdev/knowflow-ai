"""Unit tests for Phase 4 RAG Evaluation metrics, dataset, and faithfulness scoring."""

from app.evaluation.dataset import GOLDEN_BENCHMARK_CASES
from app.evaluation.faithfulness import evaluate_faithfulness
from app.evaluation.metrics import (
    calculate_hit_rate,
    calculate_mrr,
    calculate_ndcg_at_k,
    calculate_precision_at_k,
    calculate_recall_at_k,
)


def test_retrieval_ranking_metrics():
    retrieved = ["doc_a", "doc_b", "doc_c", "doc_d", "doc_e"]

    # Hit Rate @ K
    assert calculate_hit_rate(retrieved, "doc_a", k=1) == 1.0
    assert calculate_hit_rate(retrieved, "doc_b", k=1) == 0.0
    assert calculate_hit_rate(retrieved, "doc_b", k=2) == 1.0
    assert calculate_hit_rate(retrieved, "doc_z", k=5) == 0.0

    # Precision @ K & Recall @ K
    relevant = ["doc_b", "doc_d"]
    # Top 3 retrieved: ['doc_a', 'doc_b', 'doc_c'] -> 1 relevant ('doc_b')
    assert calculate_precision_at_k(retrieved, relevant, k=3) == round(1 / 3, 4) or abs(
        calculate_precision_at_k(retrieved, relevant, k=3) - 0.3333
    ) < 0.01
    # Recall @ 3: 1 out of 2 relevant docs found -> 0.5
    assert calculate_recall_at_k(retrieved, relevant, k=3) == 0.5

    # Mean Reciprocal Rank (MRR)
    # 'doc_c' is at rank 3 -> 1/3
    assert abs(calculate_mrr(retrieved, "doc_c") - 0.3333) < 0.01
    assert calculate_mrr(retrieved, "doc_a") == 1.0
    assert calculate_mrr(retrieved, "doc_z") == 0.0

    # NDCG @ 5
    ndcg = calculate_ndcg_at_k(retrieved, ["doc_a"], k=5)
    assert ndcg == 1.0  # Top rank matches ideal


def test_ndcg_normalization_and_bounds():
    """Unit test confirming NDCG output range is strictly bounded in [0.0, 1.0]
    and correctly normalized against ideal DCG (IDCG), specifically verifying that
    duplicate document chunks cannot artificially inflate DCG above IDCG.
    """
    # 1. Perfect retrieval: top-1 is relevant
    ndcg_perfect = calculate_ndcg_at_k(["doc_1", "doc_2"], ["doc_1"], k=5)
    assert ndcg_perfect == 1.0

    # 2. Duplicate chunks from same document (bug regression test)
    # Previously, multiple citations from doc_1 inflated DCG to > 2.0 while IDCG was 1.0
    duplicate_retrieved = ["doc_1", "doc_1", "doc_1", "doc_2", "doc_3"]
    ndcg_dup = calculate_ndcg_at_k(duplicate_retrieved, ["doc_1"], k=5)
    assert ndcg_dup == 1.0
    assert 0.0 <= ndcg_dup <= 1.0

    # 3. Sub-optimal ranks: relevant document appears at rank 2
    # DCG = 1 / log2(3) = ~0.6309, IDCG = 1 / log2(2) = 1.0 -> NDCG = ~0.6309
    ndcg_rank2 = calculate_ndcg_at_k(["other", "doc_1", "doc_1"], ["doc_1"], k=5)
    assert 0.63 < ndcg_rank2 < 0.64
    assert 0.0 <= ndcg_rank2 <= 1.0

    # 4. Relevant document appears at rank 3
    # DCG = 1 / log2(4) = 0.5, IDCG = 1.0 -> NDCG = 0.5
    ndcg_rank3 = calculate_ndcg_at_k(["other1", "other2", "doc_1"], ["doc_1"], k=5)
    assert abs(ndcg_rank3 - 0.5) < 1e-6
    assert 0.0 <= ndcg_rank3 <= 1.0

    # 5. Zero hits / disjoint sets
    ndcg_zero = calculate_ndcg_at_k(["x", "y", "z"], ["doc_1"], k=5)
    assert ndcg_zero == 0.0

    # 6. Multiple relevant documents
    # Relevant = ["a", "b"], Retrieved = ["a", "x", "b"]
    # IDCG = 1/log2(2) + 1/log2(3) = 1.0 + 0.63093 = 1.63093
    # DCG = 1/log2(2) + 0 + 1/log2(4) = 1.0 + 0.5 = 1.5
    # NDCG = 1.5 / 1.63093 = ~0.9197
    ndcg_multi = calculate_ndcg_at_k(["a", "x", "b"], ["a", "b"], k=5)
    assert 0.91 < ndcg_multi < 0.93
    assert 0.0 <= ndcg_multi <= 1.0

    # 7. Edge cases: empty relevant list or k <= 0
    assert calculate_ndcg_at_k(["a"], [], k=5) == 0.0
    assert calculate_ndcg_at_k(["a"], ["a"], k=0) == 0.0



def test_faithfulness_evaluation_in_scope_supported():
    answer = "Refrigerated storage must be strictly maintained between +2.0°C and +8.0°C."
    context = [
        "Clinical Operations SOP Section 1: Refrigerated storage must be strictly maintained between +2.0°C and +8.0°C."
    ]

    result = evaluate_faithfulness(
        answer=answer,
        context_excerpts=context,
        is_out_of_scope=False,
        is_grounded=True,
        grounding_status="VERIFIED",
    )

    assert result.is_faithful is True
    assert result.faithfulness_score >= 0.75
    assert result.is_false_positive is False
    assert result.is_false_negative is False


def test_faithfulness_reporting_false_positive_and_negative():
    # 1. False Positive: In-scope query was refused
    fp_result = evaluate_faithfulness(
        answer="I refuse to answer because no SOP exists.",
        context_excerpts=[],
        is_out_of_scope=False,
        is_grounded=False,
        grounding_status="REFUSED_INSUFFICIENT_EVIDENCE",
    )
    assert fp_result.is_false_positive is True
    assert fp_result.is_false_negative is False
    assert fp_result.is_faithful is False

    # 2. False Negative: Out-of-scope query was answered (hallucination)
    fn_result = evaluate_faithfulness(
        answer="Argentina won the 2022 FIFA World Cup in Qatar.",
        context_excerpts=["General company policy"],
        is_out_of_scope=True,
        is_grounded=True,
        grounding_status="VERIFIED",
    )
    assert fn_result.is_false_negative is True
    assert fn_result.is_false_positive is False
    assert fn_result.is_faithful is False

    # 3. Correct Refusal: Out-of-scope query properly refused
    correct_refusal = evaluate_faithfulness(
        answer="Under Grounded Answering Policy, no verified SOP answers this question.",
        context_excerpts=[],
        is_out_of_scope=True,
        is_grounded=False,
        grounding_status="REFUSED_INSUFFICIENT_EVIDENCE",
    )
    assert correct_refusal.is_false_negative is False
    assert correct_refusal.is_false_positive is False
    assert correct_refusal.is_faithful is True


def test_golden_benchmark_dataset_integrity():
    assert len(GOLDEN_BENCHMARK_CASES) >= 12

    in_scope = [c for c in GOLDEN_BENCHMARK_CASES if not c.is_out_of_scope]
    out_of_scope = [c for c in GOLDEN_BENCHMARK_CASES if c.is_out_of_scope]

    assert len(in_scope) >= 8
    assert len(out_of_scope) >= 4

    for case in in_scope:
        assert case.expected_doc_title is not None
        assert case.question
        assert len(case.expected_keywords) > 0

    for case in out_of_scope:
        assert case.is_out_of_scope is True
        assert case.ground_truth_answer is None
