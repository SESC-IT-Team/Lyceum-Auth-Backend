from enum import Enum


class PermissionsPresetSortableField(str, Enum):
    name = 'name'

    created_at = 'created_at'
    updated_at = 'updated_at'
