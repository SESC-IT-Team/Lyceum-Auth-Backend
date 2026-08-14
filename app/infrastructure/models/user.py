from __future__ import annotations
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sesc_auth_sdk.enums import Department, DepartmentMemberPosition
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Integer,
    String
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY as PG_ARRAY
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship, attribute_mapped_collection

from app.infrastructure.models.base import Base
from app.infrastructure.models.parent_child import ParentChildModel
from sesc_auth_sdk.enums.gender import Gender
from sesc_auth_sdk.enums.role import Role
if TYPE_CHECKING:
    from app.infrastructure.models.department_member import DepartmentMemberModel

class DepartmentMemerCreator:
    def __call__(self, department: Department, position: DepartmentMemberPosition) -> DepartmentMemberModel:
        from app.infrastructure.models.department_member import DepartmentMemberModel
        return DepartmentMemberModel(department=department, position=position)

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    pk: Mapped[int] = mapped_column(Integer, nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    roles: Mapped[list[Role]] = mapped_column(PG_ARRAY(Enum(Role)), nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    letter: Mapped[str | None] = mapped_column(String(10), nullable=True)
    class_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    login: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    lives_in_dormitory: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    parents: Mapped[list[UserModel]] = relationship(
        "UserModel",
        secondary=ParentChildModel.__table__,
        primaryjoin=id == ParentChildModel.child_id,
        secondaryjoin=id == ParentChildModel.parent_id,
        back_populates="children",
    )

    children: Mapped[list[UserModel]] = relationship(
        "UserModel",
        secondary=ParentChildModel.__table__,
        primaryjoin=id == ParentChildModel.parent_id,
        secondaryjoin=id == ParentChildModel.child_id,
        back_populates="parents",
    )

    departments: Mapped[list[DepartmentMemberModel]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        collection_class=attribute_mapped_collection("department"),
    )

    department_positions: AssociationProxy[dict[Department, DepartmentMemberPosition]] = association_proxy(
        "departments",
        "position",
        creator=DepartmentMemerCreator(),
    )

    __table_args__ = (
        CheckConstraint("grade BETWEEN 8 AND 11", name="ck_grade"),
        CheckConstraint("letter ~ '^[А-Я]$'", name="ck_letter"),
    )

__all__ = ["UserModel"]