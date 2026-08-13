from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sesc_auth_sdk.enums import DepartmentMemberPosition, Department
from sqlalchemy import ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.infrastructure.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.user import UserModel

class DepartmentMemberModel(Base):
    __tablename__ = "department_members"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    department: Mapped[Department] = mapped_column(
        Enum(Department),
        nullable=False,
    )
    position: Mapped[DepartmentMemberPosition] = mapped_column(
        Enum(DepartmentMemberPosition),
        nullable=False
    )

    user: Mapped[UserModel] = relationship(back_populates="departments")

    __table_args__ = (
        UniqueConstraint("user_id", "department", name="uq_user_department"),
    )

__all__ = ["DepartmentMemberModel"]
