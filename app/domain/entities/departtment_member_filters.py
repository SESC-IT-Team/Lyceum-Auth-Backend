from sesc_auth_sdk.enums import DepartmentMemberPosition

from app.domain.entities.user_filters import UserFilters


class DepartmentMemberFilters(UserFilters):
    positions: list[DepartmentMemberPosition] | None = None