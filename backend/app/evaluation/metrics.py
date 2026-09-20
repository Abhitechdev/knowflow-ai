"""Retrieval precision, recall, and ranking evaluation metrics.
Implements Hit Rate@K, Precision@K, Recall@K, MRR, and NDCG@K.
"""

import math
from collections.abc import Sequence


def calculate_hit_rate(retrieved_docs: Sequence[str], expected_doc: str, k: int = 3) -> float:
    """Returns 1.0 if expected_doc is within top k retrieved_docs, else 0.0."""
    if not expected_doc:
        return 0.0
    top_k = retrieved_docs[:k]
    return 1.0 if expected_doc in top_k else 0.0


def calculate_precision_at_k(retrieved_docs: Sequence[str], relevant_docs: Sequence[str], k: int = 3) -> float:
    """Returns proportion of retrieved documents in top k that are relevant."""
    if k <= 0:
        return 0.0
    top_k = retrieved_docs[:k]
    if not top_k:
        return 0.0
    relevant_set = set(relevant_docs)
    hits = sum(1 for doc in top_k if doc in relevant_set)
    return hits / len(top_k)


def calculate_recall_at_k(retrieved_docs: Sequence[str], relevant_docs: Sequence[str], k: int = 3) -> float:
    """Returns proportion of all unique relevant documents retrieved in top k (bounded in [0.0, 1.0])."""
    if not relevant_docs:
        return 0.0
    top_k = retrieved_docs[:k]
    relevant_set = set(relevant_docs)
    hits = len(set(top_k) & relevant_set)
    return hits / len(relevant_set)


def calculate_mrr(retrieved_docs: Sequence[str], expected_doc: str) -> float:
    """Returns reciprocal rank of the first relevant document, or 0.0 if not found."""
    if not expected_doc:
        return 0.0
    for rank, doc in enumerate(retrieved_docs, start=1):
        if doc == expected_doc:
            return 1.0 / rank
    return 0.0


def calculate_ndcg_at_k(retrieved_docs: Sequence[str], relevant_docs: Sequence[str], k: int = 5) -> float:
    """Calculates Normalized Discounted Cumulative Gain at rank k, strictly bounded in [0.0, 1.0].
    
    Standard NDCG compares the Discounted Cumulative Gain (DCG) of retrieved items against
    the Ideal Discounted Cumulative Gain (IDCG). In document-level evaluation, each unique
    relevant document receives gain only once (duplicate chunks from the same document
    cannot artificially inflate DCG beyond IDCG).
    """
    if not relevant_docs or k <= 0:
        return 0.0

    relevant_set = set(relevant_docs)
    top_k = retrieved_docs[:k]

    dcg = 0.0
    seen_relevant = set()
    for i, doc in enumerate(top_k):
        if doc in relevant_set and doc not in seen_relevant:
            seen_relevant.add(doc)
            dcg += 1.0 / math.log2(i + 2)  # rank is i+1, discount is log2(rank + 1) = log2(i+2)

    # Ideal DCG: all unique relevant documents appear at top ranks
    idcg = 0.0
    ideal_hits = min(len(relevant_set), k)
    for i in range(ideal_hits):
        idcg += 1.0 / math.log2(i + 2)

    if idcg == 0.0:
        return 0.0
    return min(1.0, max(0.0, dcg / idcg))

