from uuid import UUID

from pydantic import BaseModel
from sesc_auth_sdk.enums.department import Department

from app.domain.entities.user import User
from app.domain.enums.department_member_position import DepartmentMemberPosition


class DepartmentMember(BaseModel):
    user: User
    position: DepartmentMemberPosition
    department: Department
