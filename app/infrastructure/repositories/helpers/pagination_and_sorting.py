from enum import StrEnum
from app.domain.enums.user_sortable_field import UserSortableField
from app.domain.entities.pagination_and_sorting import PaginationAndSorting
from typing import Callable
from sqlalchemy import UnaryExpression
from app.infrastructure.models import Base
from typing import Any
from sqlalchemy.orm import Mapped
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.selectable import Select


def apply_pagination_and_sorting[T: Select, V: StrEnum](
        query: T,
        alias: type[Base] | AliasedClass[Base],
        pagination_and_sorting: PaginationAndSorting[V]
) -> T:
    sorting_column: Mapped[Any] = getattr(alias, pagination_and_sorting.sort_by.value)
    sorting_order: Callable[[], UnaryExpression] = getattr(sorting_column, pagination_and_sorting.order.value)
    return query.order_by(sorting_order()).offset(pagination_and_sorting.offset).limit(pagination_and_sorting.limit)
