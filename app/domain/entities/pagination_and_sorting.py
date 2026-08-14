from enum import StrEnum

from pydantic import BaseModel

from app.domain.enums.sorting_order import SortingOrder


class PaginationAndSorting[T: StrEnum](BaseModel):
    offset: int
    limit: int
    sort_by: T
    order: SortingOrder