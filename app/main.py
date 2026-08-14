from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.presentation.api import router as api_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.presentation.dependencies import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    from scripts.create_admin import create_or_update_admin
    await create_or_update_admin()
    yield


app = FastAPI(title="Auth API", lifespan=lifespan, root_path=settings.root_path)
app.state.limiter = limiter


# Настройка CORS – разрешаем фронтенду отправлять куки
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # замените на реальный адрес фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# pyrefly: ignore [bad-argument-type]
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}