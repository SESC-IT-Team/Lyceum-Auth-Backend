from datetime import date
from typing import Annotated, Optional

from pydantic import BaseModel, Field, computed_field

from datetime import datetime
from uuid import UUID, uuid4

from slowapi import middleware

from app.domain.enums.departments import Department
from app.domain.enums.gender import Gender
from app.domain.enums.permission import PermissionType
from app.domain.enums.role import Role


class User(BaseModel):
    id: UUID
    last_name: str
    first_name: str
    login: str
    password_hash: str
    roles: list[Role]
    department: Department | None = None
    gender: Gender
    permissions: Annotated[list[PermissionType], Field(default_factory=list)]
    birthday: date | None = None
    middle_name: str | None = None
    grade: int | None = None
    letter: str | None = None
    graduation_year: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_allowed(self, permission: PermissionType) -> bool:
        return permission in self.permissions

    @computed_field
    def class_name(self) -> str | None:
        if not self.grade or not self.letter:
            return None
        return str(self.grade) + self.letter

    @computed_field
    def full_name(self) -> str | None:
        return self.last_name + ' ' + self.first_name + (f' {self.middle_name}' if self.middle_name else '')
