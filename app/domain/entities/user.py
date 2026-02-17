from datetime import datetime
from uuid import UUID

from app.domain.enums.gender import Gender
from app.domain.enums.role import Role


class User:
    def __init__(
        self,
        id: UUID,
        last_name: str,
        first_name: str,
        login: str,
        password_hash: str,
        role: Role,
        gender: Gender,
        middle_name: str | None = None,
        class_name: str | None = None,
        graduation_year: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = id
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.login = login
        self.password_hash = password_hash
        self.role = role
        self.gender = gender
        self.class_name = class_name
        self.graduation_year = graduation_year
        self.created_at = created_at
        self.updated_at = updated_at
