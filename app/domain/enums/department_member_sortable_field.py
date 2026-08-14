from enum import StrEnum

class DepartmentMemberSortableField(StrEnum):
    user_first_name = "user.first_name"
    user_middle_name = "user.middle_name"
    user_last_name = "user.last_name"
    user_full_name = "user.full_name"
    user_grade = "user.grade"
    user_letter = "user.letter"
    user_class_name = "user.class_name"
    user_graduation_year = "user.graduation_year"
    user_login = "user.login"
    user_gender = "user.gender"
    user_lives_in_dormitory = "user.lives_in_dormitory"
    user_created_at = "user.created_at"
    user_updated_at = "user.updated_at"
    position = "position"
    created_at = "created_at"
    updated_at = "updated_at"
