from sqlalchemy import func
from sqlalchemy import delete
from uuid import UUID

from sesc_auth_sdk.enums import Department, DepartmentMemberPosition
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, aliased

from app.application.interfaces.repositories import IDepartmentRepository
from app.domain.entities.department_member import DepartmentMember
from app.domain.entities.departtment_member_filters import DepartmentMemberFilters
from app.domain.entities.pagination_and_sorting import PaginationAndSorting
from app.domain.enums.department_member_sortable_field import DepartmentMemberSortableField
from app.infrastructure.models import DepartmentMemberModel, UserModel
from app.infrastructure.repositories.helpers.department_member_filtering import apply_department_member_filters_to_query
from app.infrastructure.repositories.helpers.pagination_and_sorting import apply_pagination_and_sorting
from app.infrastructure.repositories.user_repository import UserRepository


class DepartmentRepository(IDepartmentRepository):
    @staticmethod
    def model_to_entity(m: DepartmentMemberModel) -> DepartmentMember:
        return DepartmentMember(
            user=UserRepository.model_to_entity(m.user),
            department=m.department,
            position=m.position,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_department_members(
            self, department: Department,
            pagination_and_sorting: PaginationAndSorting[DepartmentMemberSortableField],
            department_member_filters: DepartmentMemberFilters = DepartmentMemberFilters()
    ) -> list[DepartmentMember]:
        user_model_alias = aliased(UserModel)
        query = (
            select(DepartmentMemberModel)
            .options(joinedload(DepartmentMemberModel.user.of_type(user_model_alias)))
            .where(DepartmentMemberModel.department == department)
        )
        query = apply_department_member_filters_to_query(query, DepartmentMemberModel, user_model_alias, department_member_filters)
        query = apply_pagination_and_sorting(query, pagination_and_sorting, user_model_alias, DepartmentMemberModel)
        res = (await self._session.execute(query)).scalars().all()
        return [self.model_to_entity(m) for m in res]

    async def count_department_members(
            self, department: Department,
            department_member_filters: DepartmentMemberFilters = DepartmentMemberFilters()
    ) -> int:
        user_model_alias = aliased(UserModel)
        query = (
            select(func.count())
            .select_from(DepartmentMemberModel)
            .where(DepartmentMemberModel.department == department)
        )
        query = query.join(
            user_model_alias,
            DepartmentMemberModel.user_id == user_model_alias.id
        )
        query = apply_department_member_filters_to_query(query, DepartmentMemberModel, user_model_alias, department_member_filters)
        return (await self._session.execute(query)).scalar() or 0

    async def get_department_member(
            self,
            department: Department,
            user_id: UUID
    ) -> DepartmentMember | None:
        query = (
            select(DepartmentMemberModel)
            .options(joinedload(DepartmentMemberModel.user))
            .where(DepartmentMemberModel.department == department)
            .where(DepartmentMemberModel.user_id == user_id)
        )
        res = (await self._session.execute(query)).scalar_one_or_none()
        if not res:
            return None
        return self.model_to_entity(res)

    async def update_department_member(
            self,
            department: Department,
            user_id: UUID,
            position: DepartmentMemberPosition
    ) -> DepartmentMember:
        query = (
            select(DepartmentMemberModel)
            .options(joinedload(DepartmentMemberModel.user))
            .where(DepartmentMemberModel.department == department)
            .where(DepartmentMemberModel.user_id == user_id)
        )
        res = await self._session.execute(query)
        m = res.scalar_one()
        m.position = position
        await self._session.flush()
        return self.model_to_entity(m)

    async def add_department_member(
            self,
            department: Department,
            user_id: UUID,
            position: DepartmentMemberPosition
    ) -> DepartmentMember:
        m = DepartmentMemberModel(department=department, position=position, user_id=user_id)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        await self._session.refresh(m, attribute_names=["user"])
        return self.model_to_entity(m)

    async def delete_department_member(
            self,
            department: Department,
            user_id: UUID
    ) -> None:
        query = (
            delete(DepartmentMemberModel)
            .where(DepartmentMemberModel.department == department)
            .where(DepartmentMemberModel.user_id == user_id)
        ) 
        await self._session.execute(query)
