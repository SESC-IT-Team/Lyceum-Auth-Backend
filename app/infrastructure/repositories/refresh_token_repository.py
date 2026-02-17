from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories import IRefreshTokenRepository
from app.infrastructure.models.refresh_token import RefreshTokenModel


class RefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user_id: UUID, token: str, expires_at: datetime) -> None:
        m = RefreshTokenModel(user_id=user_id, token=token, expires_at=expires_at)
        self._session.add(m)
        await self._session.flush()

    async def get_by_token(self, token: str) -> tuple[UUID, bool] | None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token == token,
                RefreshTokenModel.revoked.is_(False),
                RefreshTokenModel.expires_at > datetime.now(timezone.utc),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return (row.user_id, row.revoked)

    async def revoke_by_token(self, token: str) -> bool:
        result = await self._session.execute(select(RefreshTokenModel).where(RefreshTokenModel.token == token))
        m = result.scalar_one_or_none()
        if m is None:
            return False
        m.revoked = True
        await self._session.flush()
        return True

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        result = await self._session.execute(select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id))
        for m in result.scalars().all():
            m.revoked = True
        await self._session.flush()
