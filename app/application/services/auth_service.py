from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
import secrets
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.domain.entities.user import User
from app.domain.enums.permission import get_permissions_for_role
from app.application.interfaces.repositories import IUserRepository, IRefreshTokenRepository

# Импорт классов ротации ключей
from app.application.services.key_creator_rotor import KeyRotationManager, RotationJWT

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthService:
    def __init__(
        self,
        user_repository: IUserRepository,
        refresh_token_repository: IRefreshTokenRepository,
        key_manager: KeyRotationManager | None = None,  # Внедрение зависимости
    ):
        self._user_repo = user_repository
        self._refresh_repo = refresh_token_repository
        
        # Инициализация менеджера ключей
        self._key_manager = key_manager or KeyRotationManager(
            keys_dir=settings.jwt_keys_dir,
            storage_backend=settings.jwt_storage_backend,  # "filesystem" | "environment"
            env_prefix=settings.jwt_env_prefix,
        )
        
        # Инициализация JWT-обёртки с поддержкой ротации
        self._jwt_handler = RotationJWT(
            key_manager=self._key_manager,
            algorithm=settings.jwt_algorithm,  # "RS256"
        )

    def hash_password(self, plain: str) -> str:
        return pwd_context.hash(plain)

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def _create_access_token(self, user_id: UUID, role: str, permissions: list[str]) -> str:
        """Создание access-токена с использованием ротации ключей"""
        payload = {
            "sub": str(user_id),
            "role": role,
            "permissions": permissions,
            "type": "access",
            # iat и exp добавляются автоматически в RotationJWT
        }
        return self._jwt_handler.create_token(
            payload,
            expires_in=settings.jwt_access_expire_minutes * 60
        )

    def _create_refresh_token_string(self) -> str:
        return secrets.token_urlsafe(64)

    async def login(self, login: str, password: str) -> dict | None:
        user = await self._user_repo.get_by_login(login)
        if user is None or not self._verify_password(password, user.password_hash):
            # Логирование неудачной попытки (без пароля!)
            logger.warning(f"Неудачная попытка входа для login={login}")
            return None
        
        permissions = [p.value for p in get_permissions_for_role(user.role)]
        access_token = self._create_access_token(user.id, user.role.value, permissions)
        refresh_token = self._create_refresh_token_string()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
        
        await self._refresh_repo.create(user.id, refresh_token, expires_at)
        
        logger.info(f"Успешный вход пользователя {user.id}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.jwt_access_expire_minutes * 60,
            "token_type": "bearer",
        }

    async def logout(self, refresh_token: str) -> bool:
        result = await self._refresh_repo.revoke_by_token(refresh_token)
        if result:
            logger.debug(f"Refresh token отозван: {refresh_token[:16]}...")
        return result

    async def refresh_tokens(self, refresh_token: str) -> dict | None:
        pair = await self._refresh_repo.get_by_token(refresh_token)
        if pair is None:
            logger.warning(f"Недействительный refresh token: {refresh_token[:16]}...")
            return None
        
        user_id, _ = pair
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            logger.warning(f"Пользователь {user_id} не найден при refresh")
            return None
        
        # Rotate-on-use: отзыв старого токена
        await self._refresh_repo.revoke_by_token(refresh_token)
        
        permissions = [p.value for p in get_permissions_for_role(user.role)]
        access_token = self._create_access_token(user.id, user.role.value, permissions)
        new_refresh = self._create_refresh_token_string()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
        
        await self._refresh_repo.create(user.id, new_refresh, expires_at)
        logger.debug(f"Токены обновлены для пользователя {user.id}")
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "expires_in": settings.jwt_access_expire_minutes * 60,
            "token_type": "bearer",
        }

    def verify_access_token(self, access_token: str) -> dict | None:
        """
        Верификация access-токена с поддержкой ротации ключей.
        Автоматически определяет ключ по заголовку `kid`.
        """
        try:
            payload = self._jwt_handler.verify_token(access_token)
            
            # Валидация типа токена
            if payload.get("type") != "access":
                logger.warning(f"Неверный тип токена: {payload.get('type')}")
                return None
            
            return {
                "user_id": UUID(payload["sub"]),
                "role": payload.get("role"),
                "permissions": payload.get("permissions") or [],
            }
        except JWTError as e:
            logger.warning(f"Ошибка верификации токена: {e}")
            return None
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при верификации: {e}", exc_info=True)
            return None

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self._user_repo.get_by_id(user_id)
    
    def rotate_keys(self, new_kid: str | None = None) -> str:
        """
        Ротация ключей: генерация новой пары и активация.
        Вызовите этот метод через защищённый admin-endpoint или cron.
        """
        new_kid = self._key_manager.rotate_keys(new_kid)
        logger.info(f"Ключи ротированы, активный kid: {new_kid}")
        return new_kid

    def get_jwks(self) -> dict:
        return self._key_manager.get_jwks()

    def export_keys_to_env(self, kid: str | None = None) -> dict[str, str]:
        return self._key_manager.export_to_env(kid)