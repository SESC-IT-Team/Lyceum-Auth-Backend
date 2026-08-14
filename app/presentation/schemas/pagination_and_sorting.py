from enum import StrEnum

from pydantic import BaseModel, Field
from fastapi import Query

from app.domain.entities.pagination_and_sorting import PaginationAndSorting
from app.domain.enums.sorting_order import SortingOrder


class PaginationAndSortingQueryParams[T: StrEnum](BaseModel):
    offset: int = Field(default=Query(default=0, ge=0))
    limit: int = Field(default=Query(default=20, ge=1))
    sort_by: T = Field(default=Query(default='created_at'))
    order: SortingOrder = Field(default=Query(default=SortingOrder.descending))

    def to_entity(self) -> PaginationAndSorting[T]:
        return PaginationAndSorting(**self.model_dump())
    