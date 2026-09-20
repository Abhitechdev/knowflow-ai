"""
Security headers middleware for production hardening.

Adds HSTS, CSP, X-Frame-Options, X-Content-Type-Options, and Referrer-Policy
headers to every response. Only active when ENVIRONMENT=production.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject security response headers into every HTTP response.

    Headers applied:
    - Strict-Transport-Security (HSTS) — enforces HTTPS for 1 year.
    - Content-Security-Policy — restricts resource origins.
    - X-Frame-Options — prevents clickjacking.
    - X-Content-Type-Options — prevents MIME sniffing.
    - Referrer-Policy — controls referrer header leakage.
    - Permissions-Policy — disables unused browser features.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        # Remove server fingerprint header if present
        if "server" in response.headers:
            del response.headers["server"]
        return response
