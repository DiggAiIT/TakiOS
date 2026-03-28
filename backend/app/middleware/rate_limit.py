"""
Redis-based sliding window rate limiting middleware.

Protects AI endpoints (cost control) and global routes (DDoS mitigation).
- AI endpoints (/grade, /analyzer, /mnemonics): 10 req / 60 s per IP
- Global: 200 req / 60 s per IP

Algorithm: sliding window via ZADD + ZREMRANGEBYSCORE + ZCARD in a MULTI/EXEC pipeline.
Fail-open: if Redis is unreachable, requests are allowed through.
"""

from __future__ import annotations

import time
import logging
from typing import Tuple

import redis.asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings

logger = logging.getLogger("takios.ratelimit")

# Path fragments that identify AI endpoints
_AI_PATH_FRAGMENTS: Tuple[str, ...] = ("/grade", "/analyzer", "/mnemonics")

# Rate limits
_AI_LIMIT: int = 10
_GLOBAL_LIMIT: int = 200
_WINDOW_SECONDS: int = 60


def _get_client_ip(request: Request) -> str:
    """Return the client IP address, falling back to 'unknown'."""
    if request.client:
        return request.client.host
    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Async sliding-window rate limiter backed by Redis.

    Initialised with the ASGI app only; Redis URL is read from
    ``app.config.settings.redis_url`` at construction time.

    Fail-open policy: any Redis error (ConnectionError, TimeoutError, etc.)
    causes the middleware to allow the request and log a warning.
    """

    def __init__(self, app) -> None:  # no extra required params
        super().__init__(app)
        self._redis: aioredis.Redis = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

    def _is_ai_endpoint(self, path: str) -> bool:
        return any(fragment in path for fragment in _AI_PATH_FRAGMENTS)

    async def _check_rate_limit(
        self,
        key: str,
        limit: int,
    ) -> Tuple[bool, int, int]:
        """
        Execute a sliding-window check via MULTI/EXEC pipeline.

        Returns:
            allowed    – True if the request should proceed.
            remaining  – Requests left in the current window.
            reset_at   – Unix timestamp when the window expires.
        """
        now: float = time.time()
        window_start: float = now - _WINDOW_SECONDS
        reset_at: int = int(now) + _WINDOW_SECONDS

        async with self._redis.pipeline(transaction=True) as pipe:
            # 1. Evict entries older than the sliding window
            pipe.zremrangebyscore(key, "-inf", window_start)
            # 2. Count requests still within the window (before this one)
            pipe.zcard(key)
            # 3. Record this request
            pipe.zadd(key, {str(now): now})
            # 4. Ensure the key expires so stale data is cleaned up
            pipe.expire(key, _WINDOW_SECONDS + 1)
            results = await pipe.execute()

        current_count: int = results[1]  # ZCARD result, before ZADD
        allowed: bool = current_count < limit
        remaining: int = max(0, limit - current_count - 1) if allowed else 0
        return allowed, remaining, reset_at

    async def dispatch(self, request: Request, call_next) -> Response:
        path: str = request.url.path
        client_ip: str = _get_client_ip(request)
        is_ai: bool = self._is_ai_endpoint(path)

        tier: str = "ai" if is_ai else "global"
        limit: int = _AI_LIMIT if is_ai else _GLOBAL_LIMIT
        window_minute: int = int(time.time() // 60)
        key: str = f"ratelimit:{tier}:{client_ip}:{window_minute}"

        try:
            allowed, remaining, reset_at = await self._check_rate_limit(key, limit)
        except Exception as exc:  # ConnectionError, TimeoutError, RedisError, …
            logger.warning(
                "takios.ratelimit: Redis unavailable (%s) — failing open for ip=%s",
                exc,
                client_ip,
            )
            return await call_next(request)

        if not allowed:
            reset_at = int(time.time()) + _WINDOW_SECONDS
            logger.warning(
                "takios.ratelimit: limit exceeded ip=%s tier=%s path=%s",
                client_ip,
                tier,
                path,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": _WINDOW_SECONDS,
                },
                headers={
                    "Retry-After": str(_WINDOW_SECONDS),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                },
            )

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at)
        return response
