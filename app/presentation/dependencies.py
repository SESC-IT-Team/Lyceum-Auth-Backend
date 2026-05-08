from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.enums.permission import PermissionType
from app.application.services.permissions_preset_service import PermissionsPresetService
from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.repositories.permissions_preset_repository import PermissionsPresetRepository
from slowapi import Limiter
from slowapi.util import get_remote_address

security_bearer = HTTPBearer(auto_error=False)

limiter = Limiter(key_func=get_remote_address)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        user_repository=UserRepository(db),
        refresh_token_repository=RefreshTokenRepository(db),
    )


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(user_repository=UserRepository(db))


def get_permissions_preset_service(db: AsyncSession = Depends(get_db)) -> PermissionsPresetService:
    return PermissionsPresetService(preset_repository=PermissionsPresetRepository(db))


async def get_token_from_header_or_cookie(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer)
) -> str | None:
    """Извлекает access token из заголовка Authorization или из cookie."""
    if credentials and credentials.credentials:
        return credentials.credentials
    # fallback to cookie
    return request.cookies.get("access_token")


async def get_current_user(
        token: str | None = Depends(get_token_from_header_or_cookie),
        auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    payload = auth_service.verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = await auth_service.get_user_by_id(payload["user_id"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_permissions(required_permissions: list[PermissionType]):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if any(p not in current_user.permissions for p in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return checker
