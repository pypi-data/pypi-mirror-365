import time
import asyncio
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class BruteForceProtectMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, target_path: str = "/login", max_delay: int = 600):
        super().__init__(app)
        self.target_path = target_path
        self.max_delay = max_delay
        self.ip_attempts = defaultdict(lambda: {"count": 0, "last_ts": 0.0})
        self.ip_attempts_lock = asyncio.Lock()

    def get_delay(self, count: int) -> int:
        return min(2 ** count, self.max_delay)

    def get_client_ip(self, request: Request) -> str:
        return request.headers.get("X-Forwarded-For", request.client.host)

    async def dispatch(self, request: Request, call_next):
        if request.url.path != self.target_path:
            return await call_next(request)

        ip = self.get_client_ip(request)

        async with self.ip_attempts_lock:
            info = self.ip_attempts[ip]
            now = time.time()
            delay = self.get_delay(info["count"])

            if now - info["last_ts"] < delay:
                remaining = int(delay - (now - info["last_ts"]))
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"Too many attempts. Try again in {remaining} seconds."}
                )

        response = await call_next(request)

        if response.status_code == 401:
            async with self.ip_attempts_lock:
                self.ip_attempts[ip]["count"] += 1
                self.ip_attempts[ip]["last_ts"] = time.time()
        elif response.status_code == 200:
            async with self.ip_attempts_lock:
                if ip in self.ip_attempts:
                    del self.ip_attempts[ip]

        return response
