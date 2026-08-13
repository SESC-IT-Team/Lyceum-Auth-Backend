from sqlalchemy.orm.util import AliasedClass

from app.domain.entities.departtment_member_filters import DepartmentMemberFilters
from app.domain.entities.user_filters import UserFilters
from app.infrastructure.models import UserModel, DepartmentMemberModel
from sqlalchemy.sql.selectable import Select

from app.infrastructure.repositories.helpers.user_filtering import apply_user_filters_to_query


def apply_department_member_filters_to_query[T: Select](
        query: T,
        department_member_model_alias: type[DepartmentMemberModel] | AliasedClass[DepartmentMemberModel] = DepartmentMemberModel,
        user_model_alias: type[UserModel] | AliasedClass[UserModel] = UserModel,
        department_member_filters: DepartmentMemberFilters = DepartmentMemberFilters()
) -> T:
    query = apply_user_filters_to_query(query, user_model_alias, UserFilters(**department_member_filters.model_dump()))
    if department_member_filters.positions:
        query = query.where(department_member_model_alias.position.in_(department_member_filters.positions))
    return query