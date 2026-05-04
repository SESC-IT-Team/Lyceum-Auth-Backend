from typing import Annotated, Optional

from pydantic import BaseModel, Field

from datetime import datetime
from uuid import UUID, uuid4

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
    gender: Gender
    permissions: Annotated[list[PermissionType], Field(default_factory=list)]
    middle_name: str | None = None
    class_name: str | None = None
    graduation_year: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_allowed(self, permission: PermissionType) -> bool:
        return permission in self.permissions
