import time
import asyncio
from collections import defaultdict
from fastapi import Request, HTTPException

ip_attempts = defaultdict(lambda: {"count": 0, "last_ts": 0.0})
ip_attempts_lock = asyncio.Lock()


def get_client_ip(request: Request) -> str:
    return request.headers.get("X-Forwarded-For", request.client.host)


def get_delay(count: int) -> int:
    return min(2 ** count, 600)


async def check_brute_force(request: Request):
    ip = get_client_ip(request)
    async with ip_attempts_lock:
        info = ip_attempts[ip]
        now = time.time()
        delay = get_delay(info["count"])

        if now - info["last_ts"] < delay:
            remaining = int(delay - (now - info["last_ts"]))
            raise HTTPException(
                status_code=429,
                detail=f"Too many attempts. Try again in {remaining} seconds."
            )


async def register_failed_login(request: Request):
    ip = get_client_ip(request)
    async with ip_attempts_lock:
        ip_attempts[ip]["count"] += 1
        ip_attempts[ip]["last_ts"] = time.time()


async def clear_login_attempts(request: Request):
    ip = get_client_ip(request)
    async with ip_attempts_lock:
        if ip in ip_attempts:
            del ip_attempts[ip]
