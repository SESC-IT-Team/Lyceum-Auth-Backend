from enum import StrEnum
from app.domain.enums.mixins import UserSortableFieldsMixin

class UserSortableField(UserSortableFieldsMixin, StrEnum):
    """Contains all standard user fields."""
    pass
