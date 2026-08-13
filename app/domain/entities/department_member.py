from uuid import UUID

from pydantic import BaseModel
from sesc_auth_sdk.enums.department import Department

from app.domain.entities.user import User
from sesc_auth_sdk.enums import DepartmentMemberPosition


class DepartmentMember(BaseModel):
    user: User
    position: DepartmentMemberPosition
    department: Department
