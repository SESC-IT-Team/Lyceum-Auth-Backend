from fastapi import HTTPException
from uuid import UUID

from sesc_auth_sdk.enums.department import Department
from sesc_openfga_sdk.lyceum_openfga_service import LyceumOpenFGAService
from fastapi import status

from app.application.services.user_service import UserService
from app.domain.entities.department_member import DepartmentMember
from sesc_openfga_sdk.models import Department as OpenFGADepartment, User as OpenFGAUser

from app.domain.enums.department_member_position import DepartmentMemberPosition
from logging import getLogger

logger = getLogger(__name__)

class DepartmentService:
    def __init__(self, openfga_service: LyceumOpenFGAService,
                 user_service: UserService):
        self._openfga_service = openfga_service
        self._user_service = user_service

    async def get_department_members(self, department: Department) -> list[DepartmentMember]:
        openfga_admins = await self._openfga_service.list_subjects(OpenFGADepartment(department.value).admin(), OpenFGAUser)
        # openfga_workers = await self._openfga_service.list_subjects(OpenFGADepartment(str(department)).wor(), OpenFGAUser)
        # admins = await self._user_service.list_users(ids=list(map(lambda x: UUID(x.id), openfga_workers)))
        return [DepartmentMember(user_id=UUID(user.id), position=DepartmentMemberPosition.admin, department=department) for user in openfga_admins]

    async def get_department_member(self, department: Department, user_id: UUID) -> DepartmentMember:
        await self._user_service.check_user_exists_by_id_or_raise(user_id)
        rels = await self._openfga_service.list_relations(OpenFGADepartment(department.value), OpenFGAUser(str(user_id)), relations=list(DepartmentMemberPosition),
                                                          return_type=DepartmentMemberPosition)
        if not rels:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User provided in request in not a member of the "{department.value}" department')
        if len(rels) > 1:
            logger.error(f'User have 2 positions in 1 department user_id={user_id} department={department}')
            raise HTTPException(status_code=500, detail='Internal server error')
        return DepartmentMember(user_id=user_id, position=rels[0], department=department)

    async def update_department_member(self, department: Department, user_id: UUID, position: DepartmentMemberPosition):
        await self._user_service.check_user_exists_by_id_or_raise(user_id)
        rels = await self._openfga_service.list_relations(OpenFGADepartment(department.value), OpenFGAUser(str(user_id)), relations=list(DepartmentMemberPosition),
                                                          return_type=DepartmentMemberPosition)
        if len(rels) > 1:
            logger.error(f'User have 2 positions in 1 department user_id={user_id} department={department}')
            raise HTTPException(status_code=500, detail='Internal server error')
        if rels and rels[0] == position:
            return
        await self._openfga_service.update_relations(writes=[OpenFGADepartment(department.value).__getattribute__(position.value)(subject=OpenFGAUser(str(user_id)))],
                                                     deletes=[OpenFGADepartment(department.value).__getattribute__(rels[0].value)(subject=OpenFGAUser(str(user_id)))] if rels else [])

    async def delete_department_member(self, department: Department, user_id: UUID):
        await self._user_service.check_user_exists_by_id_or_raise(user_id)
        pos = (await self.get_department_member(department, user_id)).position
        await self._openfga_service.update_relations(deletes=[OpenFGADepartment(department.value).__getattribute__(pos.value)(subject=OpenFGAUser(str(user_id)))])

