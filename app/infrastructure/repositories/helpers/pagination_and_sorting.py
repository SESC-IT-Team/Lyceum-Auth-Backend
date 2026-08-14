from app.domain.enums.department_member_sortable_field import DepartmentMemberSortableField
from app.domain.enums.user_sortable_field import UserSortableField
from app.domain.entities.pagination_and_sorting import PaginationAndSorting
from typing import Callable
from sqlalchemy import UnaryExpression
from app.infrastructure.models import Base, UserModel, DepartmentMemberModel
from typing import Any
from sqlalchemy.orm import Mapped
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.selectable import Select

from app.infrastructure.repositories.helpers.sortable_field_mapper import map_sortable_field


def apply_pagination_and_sorting[T: Select](
        query: T,
        pagination_and_sorting: PaginationAndSorting[UserSortableField] | PaginationAndSorting[DepartmentMemberSortableField],
        user_model_alias: type[UserModel] | AliasedClass[UserModel] = UserModel,
        department_member_model_alias: type[DepartmentMemberModel] | AliasedClass[DepartmentMemberModel] = DepartmentMemberModel
) -> T:
    sorting_column: Mapped[Any] = map_sortable_field(pagination_and_sorting.sort_by, user_model_alias, department_member_model_alias)
    sorting_order: Callable[[], UnaryExpression] = getattr(sorting_column, pagination_and_sorting.order.value)
    return query.order_by(sorting_order()).offset(pagination_and_sorting.offset).limit(pagination_and_sorting.limit)
