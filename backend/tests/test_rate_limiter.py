"""Unit tests for Phase 4 Sliding Window Rate Limiter."""

import time
import pytest
from fastapi import HTTPException
from app.security.rate_limiter import SlidingWindowRateLimiter


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
