from app.presentation.dependencies import get_user_filtering_params
from app.presentation.schemas.user import UserSortingParams
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.services.user_permissions_service import UserPermissionsService
from app.domain.entities.user import User
from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.domain.enums.permission import Permissions
from app.presentation.dependencies import get_auth_service, get_user_service, require_permissions
from app.presentation.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse, UserFilteringParams

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def list_users(offset: int,
                     limit: int,
                     filtering_params: UserFilteringParams = Depends(get_user_filtering_params),
                     sorting_params: UserSortingParams = Depends(),
                     user_service: UserService = Depends(get_user_service),
                     _: User = Depends(require_permissions([Permissions.Auth.Users.read])),
                     ):
    if limit <= 0 or limit > 100:
        limit = 20
    if offset < 0:
        offset = 0
    items = await user_service.list_users(filtering_params, sorting_params,offset=offset, limit=limit)
    total = await user_service.count_users(filtering_params, sorting_params)
    return UserListResponse(
        items=[UserResponse.from_entity(e) for e in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(require_permissions([Permissions.Auth.Users.read])),
):
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.from_entity(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
    _: User = Depends(require_permissions([Permissions.Auth.Users.create])),
):
    existing = await user_service.get_by_login(body.login)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already exists",
        )
    password_hash = auth_service.hash_password(body.password)
    user = await user_service.create(
        last_name=body.last_name,
        first_name=body.first_name,
        login=body.login,
        password_hash=password_hash,
        roles=body.roles,
        gender=body.gender,
        middle_name=body.middle_name,
        grade=body.grade,
        letter=body.letter,
        graduation_year=body.graduation_year,
        birthday=body.birthday,
    )
    return UserResponse.from_entity(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permissions([Permissions.Auth.Users.update])),
):
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not UserPermissionsService.can_update_user(current_user, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't update this user")
    if body.permissions and not UserPermissionsService.are_permissions_valid(body.permissions):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permissions list is invalid")
    if body.permissions and not UserPermissionsService.is_update_allowed(current_user, user, body.permissions):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't set this list of permissions, not enough rights.")
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
        permissions=body.permissions,
        password=body.password,
        birthday=body.birthday,
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.from_entity(updated)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permissions([Permissions.Auth.Users.delete])),
):
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not UserPermissionsService.can_update_user(current_user, user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You can't delete this user")
    deleted = await user_service.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None
