from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.department_member_position import DepartmentMemberPosition


class DepartmentMemberResponse(BaseModel):
    user_id: UUID
    position: DepartmentMemberPosition

class DepartmentMemberListResponse(BaseModel):
    members: List[DepartmentMemberResponse]

class SetDepartmentMemberPositionRequest(BaseModel):
    position: DepartmentMemberPosition
