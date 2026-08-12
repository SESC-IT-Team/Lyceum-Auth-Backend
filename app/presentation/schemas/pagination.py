from pydantic import BaseModel, Field
from fastapi import Query

class PaginationQueryParams(BaseModel):
    offset: int = Field(default=Query(ge=0, default=0))
    limit: int = Field(default=Query(ge=1, default=10))