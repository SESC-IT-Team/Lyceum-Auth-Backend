from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.application.services.permissions_preset_service import PermissionsPresetService
from app.application.services.user_permissions_service import UserPermissionsService
from app.domain.entities.user import User
from app.domain.enums.permission import Permissions
from app.presentation.dependencies import get_permissions_preset_service, require_permissions
from app.presentation.schemas.permissions_preset import PermissionsPresetResponse, PermissionsPresetListResponse, \
    PermissionsPresetCreate, PermissionsPresetUpdate, PermissionsPresetFilteringParams, PermissionsPresetSortingParams

router = APIRouter(prefix="/permissions_presets", tags=["permissions_presets"])

@router.get("/{preset_id}")
async def get_preset(preset_id: UUID, preset_service: PermissionsPresetService = Depends(get_permissions_preset_service),
                     _: User = Depends(require_permissions([Permissions.Auth.PermissionsPresets.read]))) -> PermissionsPresetResponse:
    preset = await preset_service.get_by_id(preset_id)
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    return PermissionsPresetResponse.from_entity(preset)

@router.get("")
async def list_presets(offset: int, limit: int, filtering_params: PermissionsPresetFilteringParams = Depends(), sorting_params: PermissionsPresetSortingParams = Depends(),
                       preset_service: PermissionsPresetService = Depends(get_permissions_preset_service),
                       _: User = Depends(require_permissions([Permissions.Auth.PermissionsPresets.read]))) -> PermissionsPresetListResponse:
    total = await preset_service.get_count(filtering_params)
    return PermissionsPresetListResponse(items=[PermissionsPresetResponse.from_entity(preset) for preset in await preset_service.get_list(filtering_params, sorting_params, offset, limit)],
                                         offset=offset, limit=limit, total=total)

@router.post("")
async def create(body: PermissionsPresetCreate, preset_service: PermissionsPresetService = Depends(get_permissions_preset_service),
                 _: User = Depends(require_permissions([Permissions.Auth.PermissionsPresets.create]))) -> PermissionsPresetResponse:
    return PermissionsPresetResponse.from_entity(await preset_service.create(body.name, body.permissions))

@router.patch("/{preset_id}")
async def update_preset(preset_id: UUID, body: PermissionsPresetUpdate,
                        preset_service: PermissionsPresetService = Depends(get_permissions_preset_service),
                        _: User = Depends(require_permissions([Permissions.Auth.PermissionsPresets.update]))) -> PermissionsPresetResponse:
    if body.permissions and not UserPermissionsService.are_permissions_valid(body.permissions):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permissions list is invalid")
    preset = await preset_service.update(preset_id, name=body.name, permissions=body.permissions)
    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    return PermissionsPresetResponse.from_entity(preset)

@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(preset_id: UUID,
                        preset_service: PermissionsPresetService = Depends(get_permissions_preset_service),
                        _: User = Depends(require_permissions([Permissions.Auth.PermissionsPresets.delete]))) -> None:
    deleted = await preset_service.delete(preset_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    return None
