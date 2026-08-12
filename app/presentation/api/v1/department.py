from uuid import UUID

from fastapi import APIRouter, Depends
from sesc_auth_sdk.enums.department import Department
from sesc_auth_sdk.enums.scope import Scope
from sesc_auth_sdk.schemas.token import AccessTokenPayload
from fastapi import status

from app.application.services.department_service import DepartmentService
from app.presentation.dependencies import get_department_service, Auth
from app.presentation.schemas.department import DepartmentMemberListResponse, DepartmentMemberResponse, \
    SetDepartmentMemberPositionRequest

router = APIRouter(tags=["Departments"])

@router.get("/{department_name}/members")
async def get_department_members(department_name: Department,
                                 _ = Depends(Auth([Scope.auth_users_read])),
                                 department_service: DepartmentService = Depends(get_department_service)) -> DepartmentMemberListResponse:
    return DepartmentMemberListResponse(members=[DepartmentMemberResponse(**member.model_dump()) for member in
                                                 await department_service.get_department_members(department_name)])

@router.get("/{department_name}/members/me")
async def get_department_member_of_me(department_name: Department,
                                      department_service: DepartmentService = Depends(get_department_service),
                                      payload: AccessTokenPayload = Depends(Auth([Scope.profile]))) -> DepartmentMemberResponse:
    return DepartmentMemberResponse(**(await department_service.get_department_member(department_name, payload.sub)).model_dump())

@router.get("/{department_name}/members/{user_id}")
async def get_department_member(department_name: Department, user_id: UUID,
                                department_service: DepartmentService = Depends(get_department_service),
                                _ = Depends(Auth([Scope.auth_users_read]))) -> DepartmentMemberResponse:
    return DepartmentMemberResponse(**(await department_service.get_department_member(department_name, user_id)).model_dump())

@router.put("/{department_name}/members/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_department_member(department_name: Department, user_id: UUID,
                                   body: SetDepartmentMemberPositionRequest,
                                   department_service: DepartmentService = Depends(get_department_service),
                                   _ = Depends(Auth([Scope.auth_users_update]))) -> None:
    await department_service.update_department_member(department_name, user_id, body.position)

@router.delete("/{department_name}/members/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_department_member(department_name: Department, user_id: UUID,
                                   department_service: DepartmentService = Depends(get_department_service),
                                   _ = Depends(Auth([Scope.auth_users_update]))) -> None:
    await department_service.delete_department_member(department_name, user_id)
