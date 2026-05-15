from app.domain.enums.gender import Gender
from sqlalchemy import UnaryExpression
from typing import Callable
from typing import Any
from sqlalchemy.orm import Mapped
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.application.interfaces.repositories import IUserRepository
from app.domain.enums.permission import PermissionType
from app.domain.enums.role import Role
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
            birthday=m.birthday,
            gender=m.gender,
            permissions=m.permissions,
            middle_name=m.middle_name,
            grade=m.grade,
            letter=m.letter,
            graduation_year=m.graduation_year,
            department=m.department,
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
        m.grade = e.grade
        m.letter = e.letter
        m.class_name = m.class_name
        m.graduation_year = e.graduation_year
        m.permissions = e.permissions
        m.birthday = e.birthday
        m.department = e.department

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        row: UserModel | None = result.scalar_one_or_none()
        return self.model_to_entity(row) if row else None

    async def get_by_login(self, login: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.login == login))
        row: UserModel | None = result.scalar_one_or_none()
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

    async def list_(self, login: str | None = None,
                    first_name: str | None = None, middle_name: str | None = None,
                    last_name: str | None = None, full_name: str | None = None,
                    gender: Gender | None = None, roles: list[Role] | None = None,
                    permissions: list[PermissionType] | None = None,
                    grades: list[int] | None = None, letters: list[str] | None = None,
                    graduation_years: list[int] | None = None,
                    class_names: list[str] | None = None,
                    sort_by: str | None = None, order: str | None = None,
                    offset: int = 0, limit: int = 20) -> list[User]:
        if sort_by is None:
            sort_by = 'created_at'
        if order is None:
            order = 'desc'
        query = select(UserModel)
        if login:
            query = query.where(UserModel.login == login)
        if first_name:
            query = query.where(UserModel.first_name.ilike(f'%{first_name}%'))
        if middle_name:
            query = query.where(UserModel.middle_name.ilike(f'%{middle_name}%'))
        if last_name:
            query = query.where(UserModel.last_name.ilike(f'%{last_name}%'))
        if full_name:
            query = query.where(UserModel.full_name.ilike(f'%{full_name}%'))
        if gender:
            query = query.where(UserModel.gender == gender)
        if roles:
            query = query.where(UserModel.roles.overlap(roles))
        if permissions:
            query = query.where(UserModel.permissions.overlap(permissions))
        if grades:
            query = query.where(UserModel.grade.in_(grades))
        if letters:
            query = query.where(UserModel.letter.in_(letters))
        if graduation_years:
            query = query.where(UserModel.graduation_year.in_(graduation_years))
        if class_names:
            query = query.where(UserModel.class_name.in_(class_names))
        sorting_column: Mapped[Any] = getattr(UserModel, sort_by)
        sorting_order: Callable[[], UnaryExpression] = getattr(sorting_column, order)
        result = await self._session.execute(
            query.order_by(sorting_order()).offset(offset).limit(limit)
        )
        return [self.model_to_entity(m) for m in result.scalars().all()]

    async def count(self, login: str,
                    first_name: str | None = None, middle_name: str | None = None,
                    last_name: str | None = None, full_name: str | None = None,
                    gender: Gender | None = None, roles: list[Role] | None = None,
                    permissions: list[PermissionType] | None = None,
                    grades: list[int] | None = None, letters: list[str] | None = None,
                    graduation_years: list[int] | None = None,
                    class_names: list[str] | None = None) -> int:
        query = select(func.count()).select_from(UserModel)
        if login:
            query = query.where(UserModel.login == login)
        if first_name:
            query = query.where(UserModel.first_name.ilike(f'%{first_name}%'))
        if middle_name:
            query = query.where(UserModel.middle_name.ilike(f'%{middle_name}%'))
        if last_name:
            query = query.where(UserModel.last_name.ilike(f'%{last_name}%'))
        if full_name:
            query = query.where(UserModel.full_name.ilike(f'%{full_name}%'))
        if gender:
            query = query.where(UserModel.gender == gender)
        if roles:
            query = query.where(UserModel.roles.overlap(roles))
        if permissions:
            query = query.where(UserModel.permissions.overlap(permissions))
        if grades:
            query = query.where(UserModel.grade.in_(grades))
        if letters:
            query = query.where(UserModel.letter.in_(letters))
        if graduation_years:
            query = query.where(UserModel.graduation_year.in_(graduation_years))
        if class_names:
            query = query.where(UserModel.class_name.in_(class_names))
        result = await self._session.execute(query)
        return result.scalar() or 0
