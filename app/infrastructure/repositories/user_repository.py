from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.enums.gender import Gender
from app.domain.enums.role import Role
from app.application.interfaces.repositories import IUserRepository
from app.infrastructure.models.user import UserModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, m: UserModel) -> User:
        return User(
            id=m.id,
            last_name=m.last_name,
            first_name=m.first_name,
            middle_name=m.middle_name,
            login=m.login,
            password_hash=m.password_hash,
            role=m.role if isinstance(m.role, Role) else Role(m.role),
            gender=m.gender if isinstance(m.gender, Gender) else Gender(m.gender),
            class_name=m.class_name,
            graduation_year=m.graduation_year,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def get_by_login(self, login: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.login == login))
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def create(self, user: User) -> User:
        m = UserModel(
            id=user.id,
            last_name=user.last_name,
            first_name=user.first_name,
            middle_name=user.middle_name,
            login=user.login,
            password_hash=user.password_hash,
            role=user.role,
            gender=user.gender,
            class_name=user.class_name,
            graduation_year=user.graduation_year,
        )
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return self._to_entity(m)

    async def update(self, user: User) -> User:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user.id))
        m = result.scalar_one()
        m.last_name = user.last_name
        m.first_name = user.first_name
        m.middle_name = user.middle_name
        m.role = user.role
        m.gender = user.gender
        m.class_name = user.class_name
        m.graduation_year = user.graduation_year
        m.login = user.login
        m.password_hash = user.password_hash
        await self._session.flush()
        await self._session.refresh(m)
        return self._to_entity(m)

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
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(UserModel))
        return result.scalar() or 0
