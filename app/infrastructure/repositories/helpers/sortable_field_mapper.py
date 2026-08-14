from typing import Any

from sqlalchemy.orm import Mapped
from sqlalchemy.orm.util import AliasedClass

from app.domain.enums.department_member_sortable_field import DepartmentMemberSortableField
from app.domain.enums.user_sortable_field import UserSortableField
from app.infrastructure.models import UserModel, DepartmentMemberModel

def _map_user_sortable_field(sort_by: UserSortableField,
                             user_model_alias: type[UserModel] | AliasedClass[UserModel]) -> Mapped[Any]:
    return getattr(user_model_alias, sort_by.value)

def _map_department_member_sortable_field(
        sort_by: DepartmentMemberSortableField,
        user_model_alias: type[UserModel] | AliasedClass[UserModel],
        department_member_model_alias: type[DepartmentMemberModel] | AliasedClass[DepartmentMemberModel] = DepartmentMemberModel
) -> Mapped[Any]:
    if sort_by in [DepartmentMemberSortableField.updated_at, DepartmentMemberSortableField.created_at, DepartmentMemberSortableField.position]:
        return getattr(department_member_model_alias, sort_by.value)
    return getattr(user_model_alias, sort_by.value[5:])

def map_sortable_field(
        sort_by: UserSortableField | DepartmentMemberSortableField,
        user_model_alias: type[UserModel] | AliasedClass[UserModel] = UserModel,
        department_member_model_alias: type[DepartmentMemberModel] | AliasedClass[DepartmentMemberModel] = DepartmentMemberModel
) -> Mapped[Any]:
    if isinstance(sort_by, UserSortableField):
        return _map_user_sortable_field(sort_by, user_model_alias)
    return _map_department_member_sortable_field(sort_by, user_model_alias, department_member_model_alias)

