from sesc_auth_sdk.enums import Department
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.application.interfaces.repositories import IDepartmentRepository
from app.domain.entities.department_member import DepartmentMember
from app.domain.entities.departtment_member_filters import DepartmentMemberFilters
from app.domain.entities.pagination_and_sorting import PaginationAndSorting
from app.domain.enums.department_member_sortable_field import DepartmentMemberSortableField
from app.infrastructure.models import DepartmentMemberModel
from app.infrastructure.repositories.helpers.department_member_filtering import apply_department_member_filters_to_query
from app.infrastructure.repositories.helpers.pagination_and_sorting import apply_pagination_and_sorting
from app.infrastructure.repositories.user_repository import UserRepository


class DepartmentRepository(IDepartmentRepository):
    @staticmethod
    def model_to_entity(m: DepartmentMemberModel) -> DepartmentMember:
        return DepartmentMember(
            user=UserRepository.model_to_entity(m.user),
            department=m.department,
            position=m.position,)

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_department_members(
            self, department: Department,
            pagination_and_sorting: PaginationAndSorting[DepartmentMemberSortableField],
            department_member_filters: DepartmentMemberFilters = DepartmentMemberFilters()
    ) -> list[DepartmentMember]:
        query = (
            select(DepartmentMemberModel)
            .options(joinedload(DepartmentMemberModel.user))
            .where(DepartmentMemberModel.department == department)
        )
        query = apply_department_member_filters_to_query(query, department_member_filters=department_member_filters)
        query = apply_pagination_and_sorting(query, D, pagination_and_sorting=pagination_and_sorting)


