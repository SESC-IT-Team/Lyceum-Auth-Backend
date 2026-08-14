from __future__ import annotations
from datetime import datetime
from typing import List

from fastapi import Query
from pydantic import BaseModel, Field

from sesc_auth_sdk.enums import DepartmentMemberPosition

from app.domain.entities.department_member import DepartmentMember
from app.domain.entities.departtment_member_filters import DepartmentMemberFilters
from app.presentation.schemas.user import UserResponse, UserFilteringQueryParams


class DepartmentMemberResponse(BaseModel):
    user: UserResponse
    position: DepartmentMemberPosition
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: DepartmentMember) -> DepartmentMemberResponse:
        return cls(**entity.model_dump(exclude={'user',}), user=UserResponse.from_entity(entity.user))


class DepartmentMemberListResponse(BaseModel):
    members: List[DepartmentMemberResponse]
    total: int
    offset: int
    limit: int

class SetDepartmentMemberPositionRequest(BaseModel):
    position: DepartmentMemberPosition

class DepartmentMemberFilteringQueryQueryParams(UserFilteringQueryParams):
    positions: List[DepartmentMemberPosition] | None = Field(default=Query(default=None))

    def to_entity(self) -> DepartmentMemberFilters:
        return DepartmentMemberFilters(**self.model_dump())
