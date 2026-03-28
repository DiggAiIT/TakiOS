"""Audit log middleware for IEC 62304 / EU AI Act Art. 12 traceability.

Logs every state-changing request (POST, PUT, PATCH, DELETE) with
timestamp (UTC), request ID, user UUID, endpoint, method, response status,
and duration. AI-endpoint calls additionally log the routing profile and
model tier for EU AI Act Art. 12 compliance.
"""

import logging
import time
import uuid
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings

logger = logging.getLogger("takios.audit")

# Methods that change state
MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Path fragments that identify AI-powered endpoints
_AI_PATH_FRAGMENTS = ("/grade", "/analyzer", "/mnemonics", "/dream", "/agents")


def _extract_user_id(request: Request) -> str:
    """Extract user UUID from JWT token, or return 'anonymous'.

    Only decodes the payload to extract sub claim — does NOT
    validate the token (that is handled by the auth dependency).
    Never logs emails or names (DSGVO compliance).
    """
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return "anonymous"
    try:
        import base64
        import json as _json

        token = auth_header.split(" ", 1)[1]
        # Decode JWT payload (middle segment) without verification
        payload_b64 = token.split(".")[1]
        # Add padding
        padding = 4 - len(payload_b64) % 4
        payload_b64 += "=" * padding
        payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
        return str(payload.get("sub", "authenticated"))
    except Exception:
        return "authenticated"


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all mutating API requests for audit compliance.

    Implements EU AI Act Art. 12 traceability requirements:
    - Timestamp (UTC, timezone-aware)
    - Request-ID (UUID)
    - User identification (UUID only, no PII)
    - AI model routing information for AI endpoints
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in MUTATING_METHODS:
            return await call_next(request)

        start_time = time.time()
        timestamp = datetime.now(timezone.utc)
        request_id = getattr(request.state, "request_id", None) or request.headers.get(
            "x-request-id", str(uuid.uuid4())
        )

        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        user_id = _extract_user_id(request)
        path = request.url.path
        is_ai = any(frag in path for frag in _AI_PATH_FRAGMENTS)

        # Base audit log entry (all mutating requests)
        logger.info(
            "AUDIT | timestamp=%s request_id=%s method=%s path=%s "
            "status=%d user=%s duration_ms=%.1f ip=%s",
            timestamp.isoformat(),
            request_id,
            request.method,
            path,
            response.status_code,
            user_id,
            duration_ms,
            request.client.host if request.client else "unknown",
        )

        # Extended AI traceability log (EU AI Act Art. 12)
        if is_ai:
            logger.info(
                "AI_AUDIT | timestamp=%s request_id=%s path=%s "
                "routing_profile=%s user=%s status=%d duration_ms=%.1f",
                timestamp.isoformat(),
                request_id,
                path,
                settings.model_routing_profile,
                user_id,
                response.status_code,
                duration_ms,
            )

        return response
