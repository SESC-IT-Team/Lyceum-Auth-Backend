from uuid import UUID

from pydantic import BaseModel
from sesc_auth_sdk.enums import Gender, Role


class UserFilters(BaseModel):
    ids: list[UUID] | None = None
    search: str | None = None
    gender: Gender | None = None
    roles: list[Role] | None = None
    grades: list[int] | None = None
    letters: list[str] | None = None
    graduation_years: list[int] | None = None
    class_names: list[str] | None = None
    lives_in_dormitory: bool | None = None
