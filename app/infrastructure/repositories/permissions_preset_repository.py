from collections.abc import Callable
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, func, UnaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

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

    async def create(self, preset: PermissionsPreset) -> PermissionsPreset:
        m = self.entity_to_model(preset)
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

    async def delete(self, preset_id: UUID) -> bool:
        result = await self._session.execute(select(PermissionsPresetModel).where(PermissionsPresetModel.id == preset_id))
        m = result.scalar_one_or_none()
        if m is None:
            return False
        await self._session.delete(m)
        await self._session.flush()
        return True

    async def list_(self, name: Optional[str] = None,
                    sort_by: Optional[str] = None, order: Optional[str] = None,
                    offset: int = 0, limit: int = 20) -> list[PermissionsPreset]:
        if sort_by is None:
            sort_by = 'created_at'
        if order is None:
            order = 'desc'
        query = select(PermissionsPresetModel)
        if name:
            query = query.where(PermissionsPresetModel.name.ilike(f'%{name}%'))

        sorting_column: Mapped[Any] = getattr(PermissionsPresetModel, sort_by)
        sorting_order: Callable[[], UnaryExpression] = getattr(sorting_column, order)
        result = await self._session.execute(
            query.order_by(sorting_order()).offset(offset).limit(limit)
        )
        return [self.model_to_entity(m) for m in result.scalars().all()]

    async def count(self, name: str | None = None) -> int:
        query = select(func.count()).select_from(PermissionsPresetModel)
        if name:
            query = query.where(PermissionsPresetModel.name.ilike(f'%{name}%'))
        result = await self._session.execute(query)
        return result.scalar() or 0
