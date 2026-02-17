from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.domain.entities.user import User
from app.domain.enums.permission import get_permissions_for_role
from app.application.interfaces.repositories import IUserRepository, IRefreshTokenRepository

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthService:
    def __init__(
        self,
        user_repository: IUserRepository,
        refresh_token_repository: IRefreshTokenRepository,
    ):
        self._user_repo = user_repository
        self._refresh_repo = refresh_token_repository

    def hash_password(self, plain: str) -> str:
        return pwd_context.hash(plain)

    def _hash_password(self, plain: str) -> str:
        return pwd_context.hash(plain)

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def _create_access_token(self, user_id: UUID, role: str, permissions: list[str]) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_expire_minutes)
        payload = {
            "sub": str(user_id),
            "role": role,
            "permissions": permissions,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    def _create_refresh_token_string(self) -> str:
        return secrets.token_urlsafe(64)

    async def login(self, login: str, password: str) -> dict | None:
        user = await self._user_repo.get_by_login(login)
        if user is None or not self._verify_password(password, user.password_hash):
            return None
        permissions = [p.value for p in get_permissions_for_role(user.role)]
        access_token = self._create_access_token(str(user.id), user.role.value, permissions)
        refresh_token = self._create_refresh_token_string()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
        await self._refresh_repo.create(user.id, refresh_token, expires_at)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.jwt_access_expire_minutes * 60,
            "token_type": "bearer",
        }

    async def logout(self, refresh_token: str) -> bool:
        return await self._refresh_repo.revoke_by_token(refresh_token)

    async def refresh_tokens(self, refresh_token: str) -> dict | None:
        pair = await self._refresh_repo.get_by_token(refresh_token)
        if pair is None:
            return None
        user_id, _ = pair
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            return None
        await self._refresh_repo.revoke_by_token(refresh_token)
        permissions = [p.value for p in get_permissions_for_role(user.role)]
        access_token = self._create_access_token(str(user.id), user.role.value, permissions)
        new_refresh = self._create_refresh_token_string()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
        await self._refresh_repo.create(user.id, new_refresh, expires_at)
        return {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "expires_in": settings.jwt_access_expire_minutes * 60,
            "token_type": "bearer",
        }

    def verify_access_token(self, access_token: str) -> dict | None:
        try:
            payload = jwt.decode(
                access_token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            if payload.get("type") != "access":
                return None
            return {
                "user_id": UUID(payload["sub"]),
                "role": payload.get("role"),
                "permissions": payload.get("permissions") or [],
            }
        except JWTError:
            return None

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self._user_repo.get_by_id(user_id)
