from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException
import time

rate_cache = {}

LIMITS = {
    "user": 50,
    "admin": 200
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        ip = request.client.host
        now = time.time()

        window = 60

        if ip not in rate_cache:
            rate_cache[ip] = []

        rate_cache[ip] = [t for t in rate_cache[ip] if now - t < window]
        count = len(rate_cache[ip])

        if count > LIMITS["user"]:
            raise HTTPException(status_code=429, detail="Too many requests")

        rate_cache[ip].append(now)

        response = await call_next(request)
        return response
