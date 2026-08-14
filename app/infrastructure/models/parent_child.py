from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class ParentChildModel(Base):
    __tablename__ = "parent_child"

    parent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    child_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (
        CheckConstraint("parent_id != child_id", name="ck_prevent_self_parenting"),
    )


__all__ = ['ParentChildModel']