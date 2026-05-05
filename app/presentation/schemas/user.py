from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.application.services.user_permissions_service import UserPermissionsService
from app.domain.entities.user import User
from app.domain.enums.gender import Gender
from app.domain.enums.permission import PermissionType
from app.domain.enums.role import Role


class UserCreate(BaseModel):
    last_name: str
    first_name: str
    login: str
    password: str
    roles: list[Role]
    gender: Gender
    middle_name: str | None = None
    class_name: str | None = None
    graduation_year: int | None = None


class UserUpdate(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    roles: list[Role] | None = None
    gender: Gender | None = None
    class_name: str | None = None
    graduation_year: int | None = None
    permissions: list[PermissionType] | None = None


class UserResponse(BaseModel):
    id: UUID
    last_name: str
    first_name: str
    middle_name: str | None
    roles: list[Role]
    permissions: list[PermissionType]
    gender: Gender
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
