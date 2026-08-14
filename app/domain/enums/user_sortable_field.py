from enum import StrEnum

from app.domain.enums.department_member_sortable_field import DepartmentMemberSortableField


class UserSortableField(StrEnum):
    first_name = "first_name"
    middle_name = "middle_name"
    last_name = "last_name"
    full_name = "full_name"
    grade = "grade"
    letter = "letter"
    class_name = "class_name"
    graduation_year = "graduation_year"
    login = "login"
    gender = "gender"
    lives_in_dormitory = "lives_in_dormitory"
    created_at = "created_at"
    updated_at = "updated_at"

    def to_department_member_sortable_field(self) -> DepartmentMemberSortableField:
        return DepartmentMemberSortableField(f'user.{self.value}')
