from app.domain.enums.mixins import UserSortableFieldsMixin
from enum import StrEnum

class DepartmentMemberSortableField(UserSortableFieldsMixin, StrEnum):
    """Contains all user fields plus department-specific fields."""
    position = "position"
