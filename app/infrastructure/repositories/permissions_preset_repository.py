from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.permissions_preset import PermissionsPreset
from app.application.interfaces.repositories import IPermissionsPresetRepository
from app.infrastructure.models.permissions_preset import PermissionsPresetModel


class PermissionsPresetRepository(IPermissionsPresetRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def model_to_entity(m: PermissionsPresetModel) -> PermissionsPreset:
        return PermissionsPreset(
            id=m.id,
            name=m.name,
            permissions=m.permissions,
            created_at=m.created_at,
            updated_at=m.updated_at
        )

    @staticmethod
    def entity_to_model(e: PermissionsPreset) -> PermissionsPresetModel:
        return PermissionsPresetModel(**e.model_dump())

    @staticmethod
    def apply_entity_to_model(e: PermissionsPreset, m: PermissionsPresetModel) -> None:
        m.name = e.name
        m.permissions = e.permissions

    async def get_by_id(self, preset_id: UUID) -> PermissionsPreset | None:
        result = await self._session.execute(select(PermissionsPresetModel).where(PermissionsPresetModel.id == preset_id))
        row: PermissionsPresetModel | None = result.scalar_one_or_none()
        return self.model_to_entity(row) if row else None

    async def get_by_name(self, name: str) -> PermissionsPreset | None:
        result = await self._session.execute(select(PermissionsPresetModel).where(PermissionsPresetModel.name == name))
        row: PermissionsPresetModel | None = result.scalar_one_or_none()
        return self.model_to_entity(row) if row else None

    async def create(self, user: PermissionsPreset) -> PermissionsPresetModel:
        m = self.entity_to_model(user)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return self.model_to_entity(m)

    async def update(self, preset: PermissionsPreset) -> PermissionsPreset:
        result = await self._session.execute(select(PermissionsPresetModel).where(PermissionsPresetModel.id == preset.id))
        m = result.scalar_one()
        self.apply_entity_to_model(preset, m)
        await self._session.flush()
        await self._session.refresh(m)
        return self.model_to_entity(m)

    async def delete(self, user_id: UUID) -> bool:
        result = await self._session.execute(select(PermissionsPresetModel).where(PermissionsPresetModel.id == user_id))
        m = result.scalar_one_or_none()
        if m is None:
            return False
        await self._session.delete(m)
        await self._session.flush()
        return True

    async def list_(self, offset: int, limit: int) -> list[PermissionsPreset]:
        result = await self._session.execute(
            select(PermissionsPresetModel).order_by(PermissionsPresetModel.created_at.desc()).offset(offset).limit(limit)
        )
        return [self.model_to_entity(m) for m in result.scalars().all()]

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(PermissionsPresetModel))
        return result.scalar() or 0
