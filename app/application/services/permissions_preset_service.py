from uuid import UUID, uuid4

from app.domain.entities.permissions_preset import PermissionsPreset
from app.domain.enums.permission import PermissionType
from app.application.interfaces.repositories import IPermissionsPresetRepository
from app.domain.enums.permissions_preset_sortable_field import PermissionsPresetSortableField
from app.presentation.schemas.permissions_preset import PermissionsPresetFilteringParams, PermissionsPresetSortingParams


class PermissionsPresetService:
    def __init__(
            self,
            preset_repository: IPermissionsPresetRepository
    ):
        self._repo = preset_repository

    async def get_by_id(self, preset_id: UUID) -> PermissionsPreset | None:
        return await self._repo.get_by_id(preset_id)

    async def get_by_name(self, name: str) -> PermissionsPreset | None:
        return await self._repo.get_by_name(name)

    async def create(
            self,
            name: str,
            permissions: list[PermissionType],
    ) -> PermissionsPreset:
        if not permissions:
            permissions = []
        preset = PermissionsPreset(
            id=uuid4(),
            name=name,
            permissions=permissions
        )
        created = await self._repo.create(preset)
        return created

    async def update(
            self,
            preset_id: UUID,
            *,
            name: str | None = None,
            permissions: list[PermissionType] | None = None
    ) -> PermissionsPreset | None:
        preset = await self._repo.get_by_id(preset_id)
        if preset is None:
            return None
        if name:
            preset.name = name
        if permissions:
            preset.permissions = permissions
        updated = await self._repo.update(preset)
        return updated

    async def delete(self, user_id: UUID) -> bool:
        return await self._repo.delete(user_id)

    async def get_list(self, filtering_params: PermissionsPresetFilteringParams, sorting_params: PermissionsPresetSortingParams, offset: int = 0, limit: int = 20) -> list[PermissionsPreset]:
        return await self._repo.list_(filtering_params.name, sorting_params.sort_by.value, order=sorting_params.order.value, offset=offset, limit=limit)

    async def get_count(self, filtering_params: PermissionsPresetFilteringParams) -> int:
        return await self._repo.count(filtering_params.name)
