from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.enums.gender import Gender
from app.domain.enums.role import RoleType
from app.application.interfaces.repositories import IUserRepository
from app.infrastructure.models.user import UserModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def model_to_entity(m: UserModel) -> User:
        return User(
            id=m.id,
            last_name=m.last_name,
            first_name=m.first_name,
            login=m.login,
            password_hash=m.password_hash,
            roles=m.roles,
            gender=m.gender,
            permissions=m.permissions,
            middle_name=m.middle_name,
            class_name=m.class_name,
            graduation_year=m.graduation_year,
            created_at=m.created_at,
            updated_at=m.updated_at
        )

    @staticmethod
    def entity_to_model(e: User) -> UserModel:
        return UserModel(**e.model_dump())

    @staticmethod
    def apply_entity_to_model(e: User, m: UserModel) -> None:
        m.last_name = e.last_name
        m.first_name = e.first_name
        m.login = e.login
        m.password_hash = e.password_hash
        m.roles = e.roles
        m.gender = e.gender
        m.middle_name = e.middle_name
        m.class_name = e.class_name
        m.graduation_year = e.graduation_year

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        row = result.scalar_one_or_none()
        return self.model_to_entity(row) if row else None

    async def get_by_login(self, login: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.login == login))
        row = result.scalar_one_or_none()
        return self.model_to_entity(row) if row else None

    async def create(self, user: User) -> User:
        m = self.entity_to_model(user)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return self.model_to_entity(m)

    async def update(self, user: User) -> User:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user.id))
        m = result.scalar_one()
        self.apply_entity_to_model(user, m)
        await self._session.flush()
        await self._session.refresh(m)
        return self.model_to_entity(m)

    async def delete(self, user_id: UUID) -> bool:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        m = result.scalar_one_or_none()
        if m is None:
            return False
        await self._session.delete(m)
        await self._session.flush()
        return True

    async def list_(self, offset: int, limit: int) -> list[User]:
        result = await self._session.execute(
            select(UserModel).order_by(UserModel.created_at.desc()).offset(offset).limit(limit)
        )
        return [self.model_to_entity(m) for m in result.scalars().all()]

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(UserModel))
        return result.scalar() or 0
