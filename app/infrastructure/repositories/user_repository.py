from sqlalchemy import insert
from sqlalchemy import delete

from app.infrastructure.models import ParentChildModel
from app.infrastructure.repositories.helpers.sorting_and_pagination import apply_sorting_and_pagination
from app.infrastructure.repositories.helpers.user_filtering import apply_user_filters_to_query
from sesc_auth_sdk.enums.gender import Gender
from sqlalchemy import UnaryExpression
from typing import Callable
from typing import Any
from sqlalchemy.orm import Mapped, aliased
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession, session
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.selectable import Select

from app.domain.entities.user import User
from app.application.interfaces.repositories import IUserRepository
from sesc_auth_sdk.enums.role import Role
from app.infrastructure.models.user import UserModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def model_to_entity(m: UserModel) -> User:
        return User(
            id=m.id,
            pk=m.pk,
            last_name=m.last_name,
            first_name=m.first_name,
            login=m.login,
            roles=m.roles,
            birthday=m.birthday,
            gender=m.gender,
            middle_name=m.middle_name,
            grade=m.grade,
            letter=m.letter,
            graduation_year=m.graduation_year,
            lives_in_dormitory=m.lives_in_dormitory,
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
        m.roles = e.roles
        m.gender = e.gender
        m.middle_name = e.middle_name
        m.grade = e.grade
        m.letter = e.letter
        m.class_name = m.class_name
        m.graduation_year = e.graduation_year
        m.birthday = e.birthday
        m.lives_in_dormitory = e.lives_in_dormitory

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

    async def get_users(
            self, ids: list[UUID] | None = None, search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None,
            sort_by: str = 'created_at', order: str = 'desc',
            offset: int = 0, limit: int = 20
    ) -> list[User]:
        query = select(UserModel)
        query = apply_user_filters_to_query(
            query, ids=ids, search=search,
            gender=gender, roles=roles,
            grades=grades, letters=letters,
            graduation_years=graduation_years,
            class_names=class_names,
            lives_in_dormitory=lives_in_dormitory)
        query = apply_sorting_and_pagination(query, UserModel, sort_by, order, offset, limit)
        result = await self._session.execute(query)
        return [self.model_to_entity(m) for m in result.scalars().all()]

    async def count_users(
            self, ids: list[UUID] | None = None, search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None
    ) -> int:
        query = select(func.count()).select_from(UserModel)
        query = apply_user_filters_to_query(
            query, ids=ids, search=search,
            gender=gender, roles=roles,
            grades=grades, letters=letters,
            graduation_years=graduation_years,
            class_names=class_names,
            lives_in_dormitory=lives_in_dormitory)
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_user_parents(
            self, user_id: UUID, ids: list[UUID] | None = None,
            search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None,
            sort_by: str = 'created_at', order: str = 'desc',
            offset: int = 0, limit: int = 20
    ) -> list[User]:
        parent_user = aliased(UserModel, name='parent_user')
        query = (
            select(parent_user)
            .join(UserModel.parents.of_type(parent_user))
            .where(UserModel.id == user_id)
        )
        query = apply_user_filters_to_query(
            query, alias=parent_user,
            ids=ids, search=search,
            gender=gender, roles=roles,
            grades=grades, letters=letters,
            graduation_years=graduation_years,
            class_names=class_names,
            lives_in_dormitory=lives_in_dormitory)
        query = apply_sorting_and_pagination(query, parent_user, sort_by, order, offset, limit)
        result = await self._session.execute(query)
        return [self.model_to_entity(m) for m in result.scalars().all()]

    async def count_user_parents(
            self, user_id: UUID, ids: list[UUID] | None = None,
            search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None
    ) -> int:
        parent_user = aliased(UserModel, name='parent_user')
        query = (
            select(func.count()).select_from(UserModel)
            .join(UserModel.parents.of_type(parent_user))
            .where(UserModel.id == user_id)
        )
        query = apply_user_filters_to_query(
            query, alias=parent_user,
            ids=ids, search=search,
            gender=gender, roles=roles,
            grades=grades, letters=letters,
            graduation_years=graduation_years,
            class_names=class_names,
            lives_in_dormitory=lives_in_dormitory)
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def update_user_parents(
            self, user_id: UUID,
            ids_to_add: list[UUID],
            ids_to_delete: list[UUID]
    ) -> None:
        if ids_to_delete:
            await self._session.execute(delete(ParentChildModel)
                                        .where(ParentChildModel.child_id == user_id)
                                        .where(ParentChildModel.parent_id.in_(ids_to_delete)))
        if ids_to_add:
            self._session.add_all([ParentChildModel(parent_id=p_id, child_id=user_id) for p_id in ids_to_add])
            await self._session.flush()

    async def get_user_children(
            self, user_id: UUID, ids: list[UUID] | None = None,
            search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None,
            sort_by: str = 'created_at', order: str = 'desc',
            offset: int = 0, limit: int = 20
    ) -> list[User]:
        child_user = aliased(UserModel, name='child_user')
        query = (
            select(child_user)
            .join(UserModel.children.of_type(child_user))
            .where(UserModel.id == user_id)
        )
        query = apply_user_filters_to_query(
            query, alias=child_user,
            ids=ids, search=search,
            gender=gender, roles=roles,
            grades=grades, letters=letters,
            graduation_years=graduation_years,
            class_names=class_names,
            lives_in_dormitory=lives_in_dormitory)
        query = apply_sorting_and_pagination(query, child_user, sort_by, order, offset, limit)
        result = await self._session.execute(query)
        return [self.model_to_entity(m) for m in result.scalars().all()]

    async def count_user_children(
            self, user_id: UUID, ids: list[UUID] | None = None,
            search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None
    ) -> int:
        child_user = aliased(UserModel, name='child_user')
        query = (
            select(func.count()).select_from(UserModel)
            .join(UserModel.children.of_type(child_user))
            .where(UserModel.id == user_id)
        )
        query = apply_user_filters_to_query(
            query, alias=child_user,
            ids=ids, search=search,
            gender=gender, roles=roles,
            grades=grades, letters=letters,
            graduation_years=graduation_years,
            class_names=class_names,
            lives_in_dormitory=lives_in_dormitory)
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def update_user_children(
            self, user_id: UUID,
            ids_to_add: list[UUID],
            ids_to_delete: list[UUID]
    ) -> None:
        if ids_to_delete:
            await self._session.execute(delete(ParentChildModel)
                                        .where(ParentChildModel.parent_id == user_id)
                                        .where(ParentChildModel.child_id.in_(ids_to_delete)))
        if ids_to_add:
            self._session.add_all([ParentChildModel(parent_id=user_id, child_id=c_id) for c_id in ids_to_add])
            await self._session.flush()
