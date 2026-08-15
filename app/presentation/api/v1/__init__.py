from fastapi import APIRouter

from app.presentation.api.v1.department import router as department_router
from app.presentation.api.v1.user import router as user_router

router = APIRouter()
router.include_router(user_router, prefix='/users')
router.include_router(department_router, prefix='/departments')

__all__ = ["router"]
