from sesc_auth_sdk.enums.role import Role
from sesc_auth_sdk.enums.gender import Gender
from uuid import UUID

from app.domain.entities.user import User
from app.domain.enums.sorting_order import SortingOrder
from app.domain.enums.user_sortable_field import UserSortableField


class IUserRepository:
    async def get_by_id(self, user_id: UUID) -> User | None: ...
    async def get_by_login(self, login: str) -> User | None: ...
    async def create(self, user: User) -> User: ...
    async def update(self, user: User) -> User: ...
    async def delete(self, user_id: UUID) -> bool: ...
    async def get_users(
            self, ids: list[UUID] | None = None, search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None,
            sort_by: str = 'created_at', order: str = 'desc',
            offset: int = 0, limit: int = 20
    ) -> list[User]: ...
    async def count_users(
            self, ids: list[UUID] | None = None,
            search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None
    ) -> int: ...
    async def get_user_parents(
            self, user_id: UUID,
            ids: list[UUID] | None = None,
            search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None,
            sort_by: str = 'created_at', order: str = 'desc',
            offset: int = 0, limit: int = 20
    ) -> list[User]: ...
    async def count_user_parents(
            self, user_id: UUID,
            ids: list[UUID] | None = None,
            search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None
    ) -> int: ...
    async def update_user_parents(
            self, user_id: UUID,
            ids_to_add: list[UUID],
            ids_to_delete: list[UUID]
    ) -> None: ...
    async def get_user_children(
            self, user_id: UUID,
            ids: list[UUID] | None = None,
            search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None,
            sort_by: str = 'created_at', order: str = 'desc',
            offset: int = 0, limit: int = 20
    ) -> list[User]: ...
    async def count_user_children(
            self, user_id: UUID,
            ids: list[UUID] | None = None,
            search: str | None = None,
            gender: Gender | None = None, roles: list[Role] | None = None,
            grades: list[int] | None = None, letters: list[str] | None = None,
            graduation_years: list[int] | None = None,
            class_names: list[str] | None = None,
            lives_in_dormitory: bool | None = None
    ) -> int: ...
    async def update_user_children(
            self, user_id: UUID,
            ids_to_add: list[UUID],
            ids_to_delete: list[UUID]
    ) -> None: ...
