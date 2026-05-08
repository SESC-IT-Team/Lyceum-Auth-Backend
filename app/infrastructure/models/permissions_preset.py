import datetime
import uuid
from datetime import datetime

from app.domain.enums.permission import PermissionType
from app.infrastructure.models.base import Base

from sqlalchemy import DateTime, Enum, String, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PermissionsPresetModel(Base):
    __tablename__ = "permissions_presets"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    permissions: Mapped[list[PermissionType]] = mapped_column(PG_ARRAY(Enum(PermissionType)), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
