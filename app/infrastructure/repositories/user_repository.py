from app.domain.entities.user_filters import UserFilters
from app.domain.enums.user_sortable_field import UserSortableField
from app.domain.entities.pagination_and_sorting import PaginationAndSorting
from sqlalchemy import delete

from app.infrastructure.models import ParentChildModel
from app.infrastructure.repositories.helpers.pagination_and_sorting import apply_pagination_and_sorting
from app.infrastructure.repositories.helpers.user_filtering import apply_user_filters_to_query
from sqlalchemy.orm import aliased
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.application.interfaces.repositories import IUserRepository
from app.infrastructure.models.user import UserModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def model_to_entity(m: UserModel) -> User:
        return User.model_validate(m, from_attributes=True)

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
            self,
            pagination_and_sorting: PaginationAndSorting[UserSortableField],
            user_filters: UserFilters = UserFilters()
    ) -> list[User]:
        query = select(UserModel)
        query = apply_user_filters_to_query(query, user_filters=user_filters)
        query = apply_pagination_and_sorting(query, UserModel, pagination_and_sorting)
        result = await self._session.execute(query)
        return [self.model_to_entity(m) for m in result.scalars().all()]

    async def count_users(
            self,
            user_filters: UserFilters = UserFilters()
    ) -> int:
        query = select(func.count()).select_from(UserModel)
        query = apply_user_filters_to_query(query, user_filters=user_filters)
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_user_parents(
            self, user_id: UUID,
            pagination_and_sorting: PaginationAndSorting[UserSortableField],
            user_filters: UserFilters = UserFilters()
    ) -> list[User]:
        parent_user = aliased(UserModel, name='parent_user')
        query = (
            select(parent_user)
            .join(UserModel.parents.of_type(parent_user))
            .where(UserModel.id == user_id)
        )
        query = apply_user_filters_to_query(query, parent_user, user_filters)
        query = apply_pagination_and_sorting(query, parent_user, pagination_and_sorting)
        result = await self._session.execute(query)
        return [self.model_to_entity(m) for m in result.scalars().all()]

    async def count_user_parents(
            self, user_id: UUID,
            user_filters: UserFilters = UserFilters()
    ) -> int:
        parent_user = aliased(UserModel, name='parent_user')
        query = (
            select(func.count()).select_from(UserModel)
            .join(UserModel.parents.of_type(parent_user))
            .where(UserModel.id == user_id)
        )
        query = apply_user_filters_to_query(query, parent_user, user_filters)
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
            self, user_id: UUID,
            pagination_and_sorting: PaginationAndSorting[UserSortableField],
            user_filters: UserFilters = UserFilters()
    ) -> list[User]:
        child_user = aliased(UserModel, name='child_user')
        query = (
            select(child_user)
            .join(UserModel.children.of_type(child_user))
            .where(UserModel.id == user_id)
        )
        query = apply_user_filters_to_query(query, child_user, user_filters)
        query = apply_pagination_and_sorting(query, child_user, pagination_and_sorting)
        result = await self._session.execute(query)
        return [self.model_to_entity(m) for m in result.scalars().all()]

    async def count_user_children(
            self, user_id: UUID,
            user_filters: UserFilters = UserFilters()

    ) -> int:
        child_user = aliased(UserModel, name='child_user')
        query = (
            select(func.count()).select_from(UserModel)
            .join(UserModel.children.of_type(child_user))
            .where(UserModel.id == user_id)
        )
        query = apply_user_filters_to_query(query, child_user, user_filters)
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
