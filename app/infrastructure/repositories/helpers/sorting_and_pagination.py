from typing import Callable
from sqlalchemy import UnaryExpression
from app.infrastructure.models import Base
from typing import Any
from sqlalchemy.orm import Mapped
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.selectable import Select


def apply_sorting_and_pagination(query: Select,
                                 alias: type[Base] | AliasedClass[Base],
                                 sort_by: str, order: str,
                                 offset: int, limit: int) -> Select:
    sorting_column: Mapped[Any] = getattr(alias, sort_by)
    sorting_order: Callable[[], UnaryExpression] = getattr(sorting_column, order)
    return query.order_by(sorting_order()).offset(offset).limit(limit)
