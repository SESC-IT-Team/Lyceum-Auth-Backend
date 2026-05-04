from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.department import Department
from app.domain.enums.gender import Gender
from app.domain.enums.position import Position
from app.domain.enums.role import RoleType


class UserCreate(BaseModel):
    last_name: str
    first_name: str
    login: str
    password: str
    role: RoleType
    gender: Gender
    middle_name: str | None = None
    class_name: str | None = None
    graduation_year: int | None = None
    departments: list[Department] | None = None
    position: Position | None = None


class UserUpdate(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    role: RoleType | None = None
    gender: Gender | None = None
    class_name: str | None = None
    graduation_year: int | None = None
    login: str | None = None
    password: str | None = None
    departments: list[Department] | None = None
    position: Position | None = None


class UserResponse(BaseModel):
    id: UUID
    last_name: str
    first_name: str
    middle_name: str | None
    role: RoleType
    departments: list[Department] | None = None
    position: Position | None = None
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
