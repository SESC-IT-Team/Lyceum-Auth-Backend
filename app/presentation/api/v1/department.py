from app.presentation.schemas.user import UserResponse
from sesc_auth_sdk.enums import DepartmentMemberPosition
from uuid import UUID

from fastapi import APIRouter, Depends
from sesc_auth_sdk.enums import Role
from sesc_auth_sdk.enums.department import Department
from sesc_auth_sdk.enums.scope import Scope
from sesc_auth_sdk.schemas.token import AccessTokenPayload
from fastapi import status

from app.application.services.department_service import DepartmentService
from app.domain.entities.departtment_member_filters import DepartmentMemberFilters
from app.domain.entities.pagination_and_sorting import PaginationAndSorting
from app.domain.enums.department_member_sortable_field import DepartmentMemberSortableField
from app.domain.enums.user_sortable_field import UserSortableField
from app.presentation.dependencies import get_department_service, Auth, require_department_admin
from app.presentation.schemas.department import DepartmentMemberListResponse, DepartmentMemberResponse, \
    SetDepartmentMemberPositionRequest, DepartmentMemberFilteringQueryQueryParams
from app.presentation.schemas.pagination_and_sorting import PaginationAndSortingQueryParams
from app.presentation.schemas.user import UserListResponse, UserFilteringQueryParams

router = APIRouter(tags=["Departments"])

@router.get("/{department_name}/members")
async def get_department_members(
        department_name: Department,
        pagination_and_sorting_params: PaginationAndSortingQueryParams[DepartmentMemberSortableField] = Depends(),
        department_member_filtering_params: DepartmentMemberFilteringQueryQueryParams = Depends(),
        _ = Depends(Auth([Scope.auth_users_read])),
        department_service: DepartmentService = Depends(get_department_service)
) -> DepartmentMemberListResponse:
    return DepartmentMemberListResponse(members=[DepartmentMemberResponse(**member.model_dump()) for member in
                                                 await department_service.get_department_members(department_name,
                                                                                                 pagination_and_sorting_params.to_entity(),
                                                                                                 department_member_filtering_params.to_entity())],
                                        total=await department_service.count_department_members(department_name,
                                                                                                department_member_filtering_params.to_entity()),
                                        offset=pagination_and_sorting_params.offset,
                                        limit=pagination_and_sorting_params.limit)

@router.get("/{department_name}/members/me")
async def get_department_member_of_me(
        department_name: Department,
        department_service: DepartmentService = Depends(get_department_service),
        payload: AccessTokenPayload = Depends(Auth([Scope.profile]))
) -> DepartmentMemberResponse:
    return DepartmentMemberResponse.from_entity(await department_service.get_department_member(department_name, payload.sub))

@router.get("/{department_name}/members/workers")
async def get_department_workers(
        department_name: Department,
        pagination_and_sorting_params: PaginationAndSortingQueryParams[UserSortableField] = Depends(),
        user_filtering_params: UserFilteringQueryParams = Depends(),
        department_service: DepartmentService = Depends(get_department_service),
        _: AccessTokenPayload = Depends(Auth([Scope.profile])),
        __ = Depends(require_department_admin)
) -> UserListResponse:
    department_member_filtering_params = DepartmentMemberFilteringQueryQueryParams(**user_filtering_params.model_dump(), positions=[DepartmentMemberPosition.worker])
    pagination_and_sorting = PaginationAndSortingQueryParams(offset=pagination_and_sorting_params.offset,
                                                             limit=pagination_and_sorting_params.limit,
                                                             order=pagination_and_sorting_params.order,
                                                             sort_by=pagination_and_sorting_params.sort_by.to_department_member_sortable_field())
    items = await department_service.get_department_members(department_name,
                                                            pagination_and_sorting.to_entity(),
                                                            department_member_filtering_params.to_entity())
    total = await department_service.count_department_members(department_name,
                                                              department_member_filtering_params.to_entity())
    users = [UserResponse.from_entity(item.user) for item in items]
    return UserListResponse(users=users, total=total, offset=pagination_and_sorting_params.offset, limit=pagination_and_sorting_params.limit)

@router.get("/{department_name}/members/{user_id}")
async def get_department_member(
        department_name: Department, user_id: UUID,
        department_service: DepartmentService = Depends(get_department_service),
        _ = Depends(Auth([Scope.auth_users_read]).restrict_roles_and_return_user([Role.admin]))
) -> DepartmentMemberResponse:
    return DepartmentMemberResponse(**(await department_service.get_department_member(department_name, user_id)).model_dump())

@router.put("/{department_name}/members/{user_id}",status_code=status.HTTP_200_OK)
async def update_department_member(
        department_name: Department, user_id: UUID,
        body: SetDepartmentMemberPositionRequest,
        department_service: DepartmentService = Depends(get_department_service),
        _ = Depends(Auth([Scope.auth_users_update]).restrict_roles_and_return_user([Role.admin]))
) -> DepartmentMemberResponse:
    return DepartmentMemberResponse.from_entity(await department_service.update_department_member(department_name, user_id, body.position))

@router.delete("/{department_name}/members/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_department_member(
        department_name: Department, user_id: UUID,
        department_service: DepartmentService = Depends(get_department_service),
        _ = Depends(Auth([Scope.auth_users_update]).restrict_roles_and_return_user([Role.admin]))
) -> None:
    await department_service.delete_department_member(department_name, user_id)
