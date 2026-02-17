import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums.gender import Gender
from app.domain.enums.role import Role
from app.infrastructure.models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    class_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    refresh_tokens = relationship("RefreshTokenModel", back_populates="user", cascade="all, delete-orphan")
