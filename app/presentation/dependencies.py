from uuid import UUID

from sesc_auth_sdk.dependencies import LyceumAuth, create_jwks_manager_dependency
from sesc_auth_sdk.services.jwks_manager import JWKSManager
from sesc_auth_sdk.services.m2m_auth_service import M2MAuthService
from sesc_openfga_sdk.lyceum_openfga_service import LyceumOpenFGAService

from app.application.services.authentik_service import AuthentikService
from app.application.services.department_service import DepartmentService
from app.config import settings
from app.presentation.schemas.user import UserFilteringParams
from fastapi import Query
from sesc_auth_sdk.enums.role import Role
from sesc_auth_sdk.enums.gender import Gender
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.application.services.user_service import UserService
from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

jwks_manager = JWKSManager(settings.token_validation_settings)
openfga_m2m_service = M2MAuthService(settings.openfga_m2m_settings)


def get_authentik_service() -> AuthentikService:
    return AuthentikService(settings.authentik_url, settings.users_path, settings.sa_auth_admin_app_api_token)

def get_openfga_service():
    return LyceumOpenFGAService(settings.openfga_settings, openfga_m2m_service)

def get_user_service(db: AsyncSession = Depends(get_db), auth_service: AuthentikService = Depends(get_authentik_service),
                     openfga_service: LyceumOpenFGAService = Depends(get_openfga_service)) -> UserService:
    return UserService(user_repository=UserRepository(db), authentik_service=auth_service, openfga_service=openfga_service)

class Auth(LyceumAuth):
    _get_jwks_manager = create_jwks_manager_dependency(jwks_manager)

    # pyrefly: ignore [bad-override]
    async def return_user(self, token: str = Depends(LyceumAuth._get_token), user_service: UserService = Depends(get_user_service)) -> User:
        payload = await self(token)
        user = await user_service.get_user_by_id(payload.sub)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if self._allowed_roles and not any(map(lambda r: r in self._allowed_roles, user.roles)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not have any of allowed roles.")
        return user


def get_department_service(openfga_service: LyceumOpenFGAService = Depends(get_openfga_service),
                           user_service: UserService = Depends(get_user_service)):
    return DepartmentService(openfga_service, user_service)