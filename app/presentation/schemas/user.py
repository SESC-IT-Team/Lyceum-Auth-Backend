from fastapi import Query
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.application.services.user_permissions_service import UserPermissionsService
from app.domain.entities.user import User
from app.domain.enums.gender import Gender
from app.domain.enums.permission import PermissionType
from app.domain.enums.role import Role
from app.domain.enums.sorting_order import SortingOrder
from app.domain.enums.user_sortable_field import UserSortableField


class UserCreate(BaseModel):
    last_name: str
    first_name: str
    login: str
    password: str
    roles: list[Role]
    gender: Gender
    middle_name: str | None = None
    grade: int | None = None
    letter: str | None = None
    graduation_year: int | None = None


class UserUpdate(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    roles: list[Role] | None = None
    gender: Gender | None = None
    grade: int | None = None
    letter: str | None = None
    graduation_year: int | None = None
    permissions: list[PermissionType] | None = None


class UserResponse(BaseModel):
    id: UUID
    last_name: str
    first_name: str
    middle_name: str | None
    full_name: str
    gender: Gender
    roles: list[Role]
    permissions: list[PermissionType]
    gender: Gender
    grade: int | None
    letter: str | None
    class_name: str | None
    graduation_year: int | None
    login: str
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = False

    @classmethod
    def from_entity(cls, user: User):
        return cls(**user.model_dump())


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    offset: int
    limit: int


class UserFilteringParams(BaseModel):
    login: str | None = None
    last_name: str | None = None
    first_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    gender: Gender | None = None
    roles: list[Role] | None = None
    permissions: list[PermissionType] | None = None
    grades: list[int] | None = None
    letters: list[str] | None = None
    graduation_years: list[int] | None = None
    class_names: list[str] | None = None

class UserSortingParams(BaseModel):
    sort_by: UserSortableField = UserSortableField.created_at
    order: SortingOrder = SortingOrder.descending
