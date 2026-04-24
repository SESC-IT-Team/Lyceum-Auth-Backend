from datetime import datetime
from uuid import UUID, uuid4
import logging

from app.domain.entities.user import User
from app.domain.enums.department import Department
from app.domain.enums.gender import Gender
from app.domain.enums.role import Role
from app.domain.enums.position import Position
from app.application.interfaces.repositories import IUserRepository
from app.application.services.key_creator_rotor import KeyRotationManager, RotationJWT

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self, 
        user_repository: IUserRepository,
        key_manager: KeyRotationManager | None = None,  # Опционально, для отладки
    ):
        self._repo = user_repository
        self._key_manager = key_manager  # Только для чтения/отладки

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self._repo.get_by_id(user_id)

    async def get_by_login(self, login: str) -> User | None:
        return await self._repo.get_by_login(login)

    async def create(
        self,
        last_name: str,
        first_name: str,
        login: str,
        password_hash: str,
        role: Role,
        gender: Gender,
        departments: list[Department] | None = None,
        position: Position | None = None,
        middle_name: str | None = None,
        class_name: str | None = None,
        graduation_year: int | None = None,
    ) -> User:
        user = User(
            id=uuid4(),
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            login=login,
            password_hash=password_hash,
            role=role,
            gender=gender,
            departments=departments,
            position=position,
            class_name=class_name,
            graduation_year=graduation_year,
        )
        created = await self._repo.create(user)
        logger.info(f"Пользователь создан: {created.id}, login={login}")
        return created

    async def update(
        self,
        user_id: UUID,
        *,
        last_name: str | None = None,
        first_name: str | None = None,
        middle_name: str | None = None,
        role: Role | None = None,
        gender: Gender | None = None,
        class_name: str | None = None,
        graduation_year: int | None = None,
        login: str | None = None,
        password_hash: str | None = None,
        departments: list[Department] | None = None,
        position: Position | None = None,
    ) -> User | None:
        existing = await self._repo.get_by_id(user_id)
        if existing is None:
            logger.warning(f"Пользователь {user_id} не найден для обновления")
            return None
            
        user = User(
            id=existing.id,
            last_name=last_name if last_name is not None else existing.last_name,
            first_name=first_name if first_name is not None else existing.first_name,
            middle_name=middle_name if middle_name is not None else existing.middle_name,
            login=login if login is not None else existing.login,
            password_hash=password_hash if password_hash is not None else existing.password_hash,
            role=role if role is not None else existing.role,
            gender=gender if gender is not None else existing.gender,
            class_name=class_name if class_name is not None else existing.class_name,
            graduation_year=graduation_year if graduation_year is not None else existing.graduation_year,
            departments=departments if departments is not None else existing.departments,
            position=position if position is not None else existing.position,
        )
        updated = await self._repo.update(user)
        logger.info(f"Пользователь обновлён: {user_id}")
        print(updated.position)
        return updated

    async def delete(self, user_id: UUID) -> bool:
        result = await self._repo.delete(user_id)
        if result:
            logger.info(f"Пользователь удалён: {user_id}")
        return result

    async def list_users(self, offset: int = 0, limit: int = 20) -> list[User]:
        return await self._repo.list_(offset, limit)

    async def count_users(self) -> int:
        return await self._repo.count()

    # ==================== Helper methods (только для отладки/администрирования) ====================
    
    def debug_list_keys(self) -> list[str]:
        if not self._key_manager:
            return []
        return list(self._key_manager._keys.keys())
    
    def debug_active_kid(self) -> str | None:
        """Возвращает активный kid (только для отладки!)."""
        if not self._key_manager:
            return None
        return self._key_manager._active_kid