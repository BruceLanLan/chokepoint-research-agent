"""API middleware: request id, rate limit, version header."""

from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src import __version__


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        rid = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:16]
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        response.headers["X-API-Version"] = __version__
        return response


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory sliding window rate limit (per client IP)."""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # skip health for probes
        if request.url.path in {"/health", "/"}:
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        q = self._hits[ip]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.max_requests:
            return JSONResponse(
                {
                    "detail": "rate limit exceeded",
                    "limit": self.max_requests,
                    "window_seconds": self.window,
                },
                status_code=429,
                headers={"Retry-After": str(self.window)},
            )
        q.append(now)
        return await call_next(request)
