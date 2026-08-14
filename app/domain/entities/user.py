from datetime import date

from pydantic import BaseModel, computed_field

from datetime import datetime
from uuid import UUID
from sesc_auth_sdk.enums.gender import Gender
from sesc_auth_sdk.enums.role import Role


class User(BaseModel):
    id: UUID
    pk: int = -1
    last_name: str
    first_name: str
    login: str
    roles: list[Role]
    gender: Gender
    lives_in_dormitory: bool
    birthday: date | None = None
    middle_name: str | None = None
    grade: int | None = None
    letter: str | None = None
    graduation_year: int | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @computed_field
    def class_name(self) -> str | None:
        if not self.grade or not self.letter:
            return None
        return str(self.grade) + self.letter

    @computed_field
    def full_name(self) -> str:
        return self.last_name + ' ' + self.first_name + (f' {self.middle_name}' if self.middle_name else '')
