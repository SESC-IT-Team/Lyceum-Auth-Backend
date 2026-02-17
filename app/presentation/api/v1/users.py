from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.entities.user import User
from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.presentation.dependencies import get_auth_service, get_user_service, require_admin
from app.presentation.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse

router = APIRouter(prefix="/users", tags=["users"])


def _user_to_response(u: User) -> UserResponse:
    return UserResponse(
        id=u.id,
        last_name=u.last_name,
        first_name=u.first_name,
        middle_name=u.middle_name,
        role=u.role,
        gender=u.gender,
        class_name=u.class_name,
        graduation_year=u.graduation_year,
        login=u.login,
        created_at=u.created_at,
        updated_at=u.updated_at,
    )


@router.get("", response_model=UserListResponse)
async def list_users(
    offset: int = 0,
    limit: int = 20,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(require_admin),
):
    if limit <= 0 or limit > 100:
        limit = 20
    if offset < 0:
        offset = 0
    items = await user_service.list_users(offset=offset, limit=limit)
    total = await user_service.count_users()
    return UserListResponse(
        items=[_user_to_response(u) for u in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(require_admin),
):
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _user_to_response(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
    _: User = Depends(require_admin),
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
        role=body.role,
        gender=body.gender,
        middle_name=body.middle_name,
        class_name=body.class_name,
        graduation_year=body.graduation_year,
    )
    return _user_to_response(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
    _: User = Depends(require_admin),
):
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    password_hash = None
    if body.password is not None:
        password_hash = auth_service.hash_password(body.password)
    updated = await user_service.update(
        user_id,
        last_name=body.last_name,
        first_name=body.first_name,
        middle_name=body.middle_name,
        role=body.role,
        gender=body.gender,
        class_name=body.class_name,
        graduation_year=body.graduation_year,
        login=body.login,
        password_hash=password_hash,
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _user_to_response(updated)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(require_admin),
):
    deleted = await user_service.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None
