import time
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# In-memory sliding-window limiter. Swap for a Redis-backed counter (Phase 30)
# when running more than one app instance.
_requests = defaultdict(list)
WINDOW_SECONDS = 60
MAX_REQUESTS = 120


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - WINDOW_SECONDS

        _requests[client_ip] = [t for t in _requests[client_ip] if t > window_start]

        if len(_requests[client_ip]) >= MAX_REQUESTS:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again shortly."})

        _requests[client_ip].append(now)
        return await call_next(request)
