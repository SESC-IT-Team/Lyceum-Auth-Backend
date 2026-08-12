from fastapi import APIRouter

from app.presentation.api.v1.auth import router as auth_router
from app.presentation.api.v1.department import router as department_router
from app.presentation.api.v1.user import router as user_router

router = APIRouter()
router.include_router(auth_router, tags=['Auth'])
router.include_router(department_router)
router.include_router(user_router)

__all__ = ["router"]
