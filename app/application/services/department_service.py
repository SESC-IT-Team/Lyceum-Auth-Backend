from app.application.interfaces.repositories import IDepartmentRepository
from fastapi import HTTPException
from uuid import UUID

from sesc_auth_sdk.enums.department import Department
from fastapi import status

from app.application.services.user_service import UserService
from app.domain.entities.department_member import DepartmentMember

from sesc_auth_sdk.enums import DepartmentMemberPosition
from logging import getLogger

from app.domain.entities.departtment_member_filters import DepartmentMemberFilters
from app.domain.entities.pagination_and_sorting import PaginationAndSorting
from app.domain.enums.department_member_sortable_field import DepartmentMemberSortableField

logger = getLogger(__name__)

class DepartmentService:
    def __init__(
            self,
            user_service: UserService,
            repo: IDepartmentRepository
    ) -> None:
        self._repo = repo
        self._user_service = user_service

    async def get_department_members(
            self, department: Department,
            pagination_and_sorting: PaginationAndSorting[DepartmentMemberSortableField],
            department_member_filters: DepartmentMemberFilters
    ) -> list[DepartmentMember]:
        return await self._repo.get_department_members(department, pagination_and_sorting, department_member_filters)

    async def count_department_members(
            self, department: Department,
            department_member_filters: DepartmentMemberFilters
    ) -> int:
        return await self._repo.count_department_members(department, department_member_filters)

    async def get_department_member(
            self,
            department: Department,
            user_id: UUID
    ) -> DepartmentMember:
        await self._user_service.check_user_exists_by_id_or_raise(user_id)
        res = await self._repo.get_department_member(department, user_id)
        if res is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Member not found')
        return res

    async def check_department_member_exists_or_raise(
            self,
            department: Department,
            user_id: UUID
    ) -> None:
        await self._user_service.check_user_exists_by_id_or_raise(user_id)
        if not await self._repo.get_department_member(department, user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Member not found')

    async def update_department_member(
            self,
            department: Department,
            user_id: UUID,
            position: DepartmentMemberPosition
    ) -> DepartmentMember:
        await self._user_service.check_user_exists_by_id_or_raise(user_id)
        if await self._repo.get_department_member(department, user_id):
            return await self._repo.update_department_member(department, user_id, position)
        return await self._repo.add_department_member(department, user_id, position)


    async def delete_department_member(self, department: Department, user_id: UUID):
        await self._user_service.check_user_exists_by_id_or_raise(user_id)
        await self.check_department_member_exists_or_raise(department, user_id)
        await self._repo.delete_department_member(department, user_id)

