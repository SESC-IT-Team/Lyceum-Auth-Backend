from sesc_auth_sdk.enums.role import Role
from sesc_auth_sdk.enums.scope import Scope

from app.domain.enums.user_sortable_field import UserSortableField
from app.presentation.dependencies import get_user_service
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.domain.entities.user import User
from app.application.services.user_service import UserService
from app.presentation.schemas.pagination_and_sorting import PaginationAndSortingQueryParams
from app.presentation.schemas.user import UserCreate, UserInfoUpdate, UserResponse, UserListResponse, \
    UserFilteringQueryParams, UpdateUserParentsOrChildrenRequest, \
    UserPasswordUpdate
from app.presentation.dependencies import Auth
from sesc_auth_sdk.schemas.token import AccessTokenPayload

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(Auth([Scope.profile]).return_user)):
    return UserResponse.from_entity(user)

@router.get("/me/children")
async def get_my_children(
        pagination_and_sorting_query_params: PaginationAndSortingQueryParams[UserSortableField] = Depends(),
        filtering_query_params: UserFilteringQueryParams = Depends(),
        token_payload: AccessTokenPayload = Depends(Auth([Scope.auth_children_read])),
        user_service: UserService = Depends(get_user_service)
) -> UserListResponse:
    items = await user_service.get_children_by_parent_id(token_payload.sub,
                                                         pagination_and_sorting_query_params.to_entity(),
                                                         filtering_query_params.to_entity())
    total = await user_service.count_children_by_parent_id(token_payload.sub,
                                                           filtering_query_params.to_entity())
    return UserListResponse(
        users=[UserResponse.from_entity(e) for e in items],
        total=total,
        offset=pagination_and_sorting_query_params.offset,
        limit=pagination_and_sorting_query_params.limit,
    )

@router.get("/me/children/{child_id}")
async def get_my_child(child_id: UUID, token_payload: AccessTokenPayload = Depends(Auth([Scope.auth_children_read])),
                       user_service: UserService = Depends(get_user_service)):
    return UserResponse.from_entity(await user_service.get_child_of_parent(child_id, token_payload.sub))

@router.get("")
async def list_users(
        pagination_and_sorting_query_params: PaginationAndSortingQueryParams[UserSortableField] = Depends(),
        filtering_query_params: UserFilteringQueryParams = Depends(),
        user_service: UserService = Depends(get_user_service),
        _: User = Depends(Auth([Scope.auth_users_read]).restrict_roles_and_return_user([Role.admin])),
) -> UserListResponse:
    items = await user_service.list_users(pagination_and_sorting_query_params.to_entity(),
                                          filtering_query_params.to_entity())
    total = await user_service.count_users(filtering_query_params.to_entity())
    return UserListResponse(
        users=[UserResponse.from_entity(e) for e in items],
        total=total,
        offset=pagination_and_sorting_query_params.offset,
        limit=pagination_and_sorting_query_params.limit,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        body: UserCreate,
        user_service: UserService = Depends(get_user_service),
        _: User = Depends(Auth([Scope.auth_users_create]).restrict_roles_and_return_user([Role.admin]))
):
    user = await user_service.create(
        last_name=body.last_name,
        first_name=body.first_name,
        login=body.login,
        roles=body.roles,
        gender=body.gender,
        middle_name=body.middle_name,
        grade=body.grade,
        letter=body.letter,
        graduation_year=body.graduation_year,
        birthday=body.birthday,
        lives_in_dormitory=body.lives_in_dormitory
    )
    return UserResponse.from_entity(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(Auth([Scope.auth_users_read]).restrict_roles_and_return_user([Role.admin])),
):
    user = await user_service.get_user_by_id(user_id)
    return UserResponse.from_entity(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    body: UserInfoUpdate,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(Auth([Scope.auth_users_update])),
) -> UserResponse:
    updated = await user_service.update_user(
        user_id,
        last_name=body.last_name,
        first_name=body.first_name,
        middle_name=body.middle_name,
        roles=body.roles,
        gender=body.gender,
        grade=body.grade,
        letter=body.letter,
        graduation_year=body.graduation_year,
        birthday=body.birthday,
        lives_in_dormitory=body.lives_in_dormitory
    )
    return UserResponse.from_entity(updated)


@router.put('/{user_id}/password', status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
        user_id: UUID,
        body: UserPasswordUpdate,
        _: User = Depends(Auth([Scope.auth_users_update]).restrict_roles_and_return_user([Role.admin])),
        user_service: UserService = Depends(get_user_service)
) -> None:
    await user_service.update_password(user_id, body.password)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: UUID,
        user_service: UserService = Depends(get_user_service),
        _: User = Depends(Auth([Scope.auth_users_delete])),
) -> None:
    await user_service.delete(user_id)

@router.get('/{user_id}/parents')
async def get_user_parents(
        user_id: UUID,
        pagination_and_sorting_query_params: PaginationAndSortingQueryParams[UserSortableField] = Depends(),
        filtering_query_params: UserFilteringQueryParams = Depends(),
        user_service: UserService = Depends(get_user_service),
        _: User = Depends(Auth([Scope.auth_users_read]).restrict_roles_and_return_user([Role.admin]))
) -> UserListResponse:
    items = await user_service.get_parents_by_child_id(user_id,
                                                       pagination_and_sorting_query_params.to_entity(),
                                                       filtering_query_params.to_entity())
    total = await user_service.count_parents_by_child_id(user_id,
                                                         filtering_query_params.to_entity())
    return UserListResponse(
        users=[UserResponse.from_entity(e) for e in items],
        total=total,
        offset=pagination_and_sorting_query_params.offset,
        limit=pagination_and_sorting_query_params.limit,
    )

@router.patch('/{user_id}/parents', status_code=status.HTTP_204_NO_CONTENT)
async def update_user_parents(
        user_id: UUID,
        body: UpdateUserParentsOrChildrenRequest,
        user_service: UserService = Depends(get_user_service),
        _: User = Depends(Auth([Scope.auth_users_read]).restrict_roles_and_return_user([Role.admin]))
) -> None:
    await user_service.update_parents_by_child_id(user_id, body.ids_to_add, body.ids_to_delete)

@router.get('/{user_id}/children')
async def get_user_children(
        user_id: UUID,
        pagination_and_sorting_query_params: PaginationAndSortingQueryParams[UserSortableField] = Depends(),
        filtering_query_params: UserFilteringQueryParams = Depends(),
        user_service: UserService = Depends(get_user_service),
        _: User = Depends(Auth([Scope.auth_users_read]).restrict_roles_and_return_user([Role.admin]))
) -> UserListResponse:
    items = await user_service.get_children_by_parent_id(user_id,
                                                         pagination_and_sorting_query_params.to_entity(),
                                                         filtering_query_params.to_entity())
    total = await user_service.count_children_by_parent_id(user_id,
                                                           filtering_query_params.to_entity())
    return UserListResponse(
        users=[UserResponse.from_entity(e) for e in items],
        total=total,
        offset=pagination_and_sorting_query_params.offset,
        limit=pagination_and_sorting_query_params.limit,
    )

@router.patch('/{user_id}/children', status_code=status.HTTP_204_NO_CONTENT)
async def update_user_parents(
        user_id: UUID,
        body: UpdateUserParentsOrChildrenRequest,
        user_service: UserService = Depends(get_user_service),
        _: User = Depends(Auth([Scope.auth_users_read]).restrict_roles_and_return_user([Role.admin]))
) -> None:
    await user_service.update_children_by_parent_id(user_id, body.ids_to_add, body.ids_to_delete)

