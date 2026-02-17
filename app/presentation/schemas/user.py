from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.gender import Gender
from app.domain.enums.role import Role


class UserCreate(BaseModel):
    last_name: str
    first_name: str
    login: str
    password: str
    role: Role
    gender: Gender
    middle_name: str | None = None
    class_name: str | None = None
    graduation_year: int | None = None


class UserUpdate(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    role: Role | None = None
    gender: Gender | None = None
    class_name: str | None = None
    graduation_year: int | None = None
    login: str | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: UUID
    last_name: str
    first_name: str
    middle_name: str | None
    role: Role
    gender: Gender
    class_name: str | None
    graduation_year: int | None
    login: str
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = False


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    offset: int
    limit: int
