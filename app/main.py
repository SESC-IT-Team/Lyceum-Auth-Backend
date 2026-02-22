from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.presentation.api.v1 import auth, users

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.presentation.dependencies import limiter
@asynccontextmanager
async def lifespan(app: FastAPI):
    from scripts.create_admin import create_admin
    await create_admin()
    yield


app = FastAPI(title="Auth API", lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
@app.get("/health")
async def health():
    return {"status": "ok"}
