import time
import asyncio
from collections import defaultdict
from fastapi import Request, HTTPException

ip_attempts = defaultdict(lambda: {"count": 0, "last_ts": 0.0})
ip_attempts_lock = asyncio.Lock()

def get_delay(count: int) -> int:
    return min(2 ** count, 600)

def get_client_ip(request: Request) -> str:
    return request.headers.get("X-Forwarded-For", request.client.host)

async def check_rate_limit(request: Request):
    ip = get_client_ip(request)
    info = ip_attempts[ip]
    delay = get_delay(info["count"])
    now = time.time()

    if now - info["last_ts"] < delay:
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Try again in {int(delay - (now - info['last_ts']))} seconds."
        )

async def on_login_failure(request: Request):
    ip = get_client_ip(request)
    async with ip_attempts_lock:
        ip_attempts[ip]["count"] += 1
        ip_attempts[ip]["last_ts"] = time.time()

async def on_login_success(request: Request):
    ip = get_client_ip(request)
    async with ip_attempts_lock:
        if ip in ip_attempts:
            del ip_attempts[ip]
