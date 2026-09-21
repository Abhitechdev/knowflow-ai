"""Sliding-Window Rate Limiting & Abuse Protection.
Tracks requests per IP and per authenticated user, returning HTTP 429
with Retry-After header when configured limits are exceeded.
"""

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Maps key -> list of timestamps
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """Checks if a request under 'key' is allowed.
        Returns: (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Prune timestamps outside the current sliding window
        valid_timestamps = [ts for ts in self.requests[key] if ts > window_start]
        self.requests[key] = valid_timestamps

        if len(valid_timestamps) >= self.max_requests:
            oldest_timestamp = valid_timestamps[0]
            retry_after = max(1, int(oldest_timestamp + self.window_seconds - now))
            return False, retry_after

        self.requests[key].append(now)
        return True, 0

    def check_limit(self, key: str):
        """Raises HTTPException(429) if limit exceeded."""
        allowed, retry_after = self.is_allowed(key)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds}s. Please retry in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )


# Global instances for endpoints
chat_rate_limiter = SlidingWindowRateLimiter(max_requests=25, window_seconds=60)
search_rate_limiter = SlidingWindowRateLimiter(max_requests=60, window_seconds=60)
admin_rate_limiter = SlidingWindowRateLimiter(max_requests=50, window_seconds=60)


def _get_client_key(request: Request, prefix: str) -> str:
    """Extracts a reliable client identifier from X-Forwarded-For or Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header:
        # Use token signature/tail for per-user limiting
        return f"{prefix}:auth:{auth_header[-32:] if len(auth_header) > 32 else auth_header}"
    
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "127.0.0.1"
    return f"{prefix}:ip:{client_ip}"


async def rate_limit_chat(request: Request):
    key = _get_client_key(request, "chat")
    chat_rate_limiter.check_limit(key)


async def rate_limit_search(request: Request):
    key = _get_client_key(request, "search")
    search_rate_limiter.check_limit(key)


async def rate_limit_admin(request: Request):
    key = _get_client_key(request, "admin")
    admin_rate_limiter.check_limit(key)

