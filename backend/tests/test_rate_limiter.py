"""Unit tests for Phase 4 Sliding Window Rate Limiter."""

import time

import pytest
from app.security.rate_limiter import SlidingWindowRateLimiter
from fastapi import HTTPException


def test_sliding_window_rate_limiter_allows_up_to_max():
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=10)
    key = "user_test_1"

    # Send 5 requests - all must be allowed
    for i in range(5):
        allowed, retry_after = limiter.is_allowed(key)
        assert allowed is True
        assert retry_after == 0

    # 6th request must be blocked
    allowed, retry_after = limiter.is_allowed(key)
    assert allowed is False
    assert retry_after > 0


def test_sliding_window_rate_limiter_resets_after_window():
    # Use very short window for fast testing
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=1)
    key = "user_test_2"

    assert limiter.is_allowed(key)[0] is True
    assert limiter.is_allowed(key)[0] is True
    assert limiter.is_allowed(key)[0] is False

    # Wait for window to expire
    time.sleep(1.1)

    # Now allowed again
    assert limiter.is_allowed(key)[0] is True


def test_check_limit_raises_http_429():
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=10)
    key = "user_test_3"

    limiter.check_limit(key)  # 1st request ok

    # 2nd request raises 429
    with pytest.raises(HTTPException) as exc_info:
        limiter.check_limit(key)

    assert exc_info.value.status_code == 429
    assert "Retry-After" in exc_info.value.headers


def test_endpoint_rate_limit_integration(client):
    from app.security.rate_limiter import search_rate_limiter
    # Configure low limit for immediate verification
    orig_max = search_rate_limiter.max_requests
    orig_window = search_rate_limiter.window_seconds
    try:
        search_rate_limiter.max_requests = 3
        search_rate_limiter.window_seconds = 30
        search_rate_limiter.requests.clear()

        # Send 3 requests - should pass or return 401/422/200 but NOT 429
        for _ in range(3):
            res = client.get("/api/v1/search?query=test")
            assert res.status_code != 429

        # 4th request must be rejected with 429
        res = client.get("/api/v1/search?query=test")
        assert res.status_code == 429
        assert "Retry-After" in res.headers
        assert "Rate limit exceeded" in res.json()["detail"]
    finally:
        search_rate_limiter.max_requests = orig_max
        search_rate_limiter.window_seconds = orig_window
        search_rate_limiter.requests.clear()

