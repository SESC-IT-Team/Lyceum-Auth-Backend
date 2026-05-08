from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.permission import PermissionType


class PermissionsPreset(BaseModel):
    id: UUID
    name: str
    permissions: list[PermissionType]

    created_at: datetime | None = None
    updated_at: datetime | None = None
