from datetime import date
from datetime import datetime
from uuid import UUID
from fastapi import Query

from pydantic import BaseModel, Field
from app.domain.entities.user import User
from sesc_auth_sdk.enums.gender import Gender
from sesc_auth_sdk.enums.role import Role

from app.domain.entities.user_filters import UserFilters
from app.domain.enums.sorting_order import SortingOrder
from app.domain.enums.user_sortable_field import UserSortableField


class UserCreate(BaseModel):
    last_name: str
    first_name: str
    login: str
    roles: list[Role]
    gender: Gender
    lives_in_dormitory: bool = False
    middle_name: str | None = None
    grade: int | None = None
    letter: str | None = None
    graduation_year: int | None = None
    birthday: date | None = None


class UserInfoUpdate(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    roles: list[Role] | None = None
    gender: Gender | None = None
    lives_in_dormitory: bool | None = None
    grade: int | None = None
    letter: str | None = None
    graduation_year: int | None = None
    birthday: date | None = None


class UserResponse(BaseModel):
    id: UUID
    last_name: str
    first_name: str
    middle_name: str | None
    full_name: str
    gender: Gender
    roles: list[Role]
    lives_in_dormitory: bool
    birthday: date | None
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
    users: list[UserResponse]
    total: int
    offset: int
    limit: int

class UserFilteringParams(BaseModel):
    ids: list[UUID] | None = Field(default=Query(default=None, description='Filter users by IDs'))
    search: str | None = Field(default=Query(default=None, description='Filter users by login|names'))
    gender: Gender | None = Field(default=Query(default=None, description='Filter users by gender'))
    roles: list[Role] | None = Field(default=Query(default=None, description='Filter users by roles'))
    grades: list[int] | None = Field(default=Query(default=None, description='Filter users by grades'))
    letters: list[str] | None = Field(default=Query(default=None, description='Filter users by letters'))
    graduation_years: list[int] | None = Field(default=Query(default=None, description='Filter users by graduation_years'))
    class_names: list[str] | None = Field(default=Query(default=None, description='Filter users by class_names'))
    lives_in_dormitory: bool | None = Field(default=Query(default=None, description='Filter users by lives_in_dormitory attr'))

    def to_entity(self) -> UserFilters:
        return UserFilters(**self.model_dump())

class UpdateUserParentsOrChildrenRequest(BaseModel):
    ids_to_add: list[UUID] | None = None
    ids_to_delete: list[UUID] | None = None

class UserPasswordUpdate(BaseModel):
    password: str
