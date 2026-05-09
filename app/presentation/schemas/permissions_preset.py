from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from app.domain.entities.permissions_preset import PermissionsPreset
from app.domain.enums.permission import PermissionType
from app.domain.enums.permissions_preset_sortable_field import PermissionsPresetSortableField
from app.domain.enums.sorting_order import SortingOrder


class PermissionsPresetCreate(BaseModel):
    name: str
    permissions: list[PermissionType]

class PermissionsPresetUpdate(BaseModel):
    name: str | None = None
    permissions: list[PermissionType] | None = None

class PermissionsPresetResponse(BaseModel):
    id: UUID
    name: str
    permissions: list[PermissionType]

    @classmethod
    def from_entity(cls, preset: PermissionsPreset):
        return cls(**preset.model_dump())

class PermissionsPresetListResponse(BaseModel):
    items: list[PermissionsPresetResponse]
    total: int
    offset: int
    limit: int

class PermissionsPresetFilteringParams(BaseModel):
    name: str | None = None

class PermissionsPresetSortingParams(BaseModel):
    sort_by: PermissionsPresetSortableField = PermissionsPresetSortableField.created_at
    order: SortingOrder = SortingOrder.descending
