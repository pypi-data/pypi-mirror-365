# fastapi-login-shield

A minimal FastAPI middleware to prevent brute-force login attempts based on client IP.

## Features

- IP-based login rate limiting
- Exponential backoff delays
- Lightweight, no Redis required

## Usage

```python
from fastapi import FastAPI, Request
from fastapi_login_shield import LoginShieldMiddleware, register_login_result

app = FastAPI()
app.add_middleware(LoginShieldMiddleware, login_path="/login")

@app.post("/login")
async def login(request: Request):
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    ...
    await register_login_result(ip, success=True|False)
```
