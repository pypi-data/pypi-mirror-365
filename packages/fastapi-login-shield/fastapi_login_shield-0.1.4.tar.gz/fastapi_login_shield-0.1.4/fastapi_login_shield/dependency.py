from fastapi import Depends, Request
from .core import check_rate_limit

async def login_shield_dependency(request: Request):
    await check_rate_limit(request)
