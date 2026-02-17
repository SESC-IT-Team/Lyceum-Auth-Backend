from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.enums.permission import Permission
from app.domain.enums.role import Role
from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository

security_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        user_repository=UserRepository(db),
        refresh_token_repository=RefreshTokenRepository(db),
    )


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(user_repository=UserRepository(db))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    payload = auth_service.verify_access_token(credentials.credentials)
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


def require_permission(permission: Permission):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        from app.domain.enums.permission import get_permissions_for_role
        perms = get_permissions_for_role(current_user.role)
        if permission not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return checker


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only",
        )
    return current_user
