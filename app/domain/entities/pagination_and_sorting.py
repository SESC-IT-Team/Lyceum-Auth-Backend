from enum import StrEnum

from pydantic import BaseModel

from app.domain.enums.sorting_order import SortingOrder


class PaginationAndSortingParams[T: StrEnum](BaseModel):
    offset: int = 0
    limit: int = 10
    sort_by: T
    order: SortingOrder