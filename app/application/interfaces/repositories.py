from sesc_auth_sdk.enums import Department, DepartmentMemberPosition
from uuid import UUID
from app.domain.entities.department_member import DepartmentMember
from app.domain.entities.departtment_member_filters import DepartmentMemberFilters
from app.domain.entities.pagination_and_sorting import PaginationAndSorting
from app.domain.entities.user import User
from app.domain.entities.department_member_filters import UserFilters
from app.domain.enums.department_member_sortable_field import DepartmentMemberSortableField
from app.domain.enums.user_sortable_field import UserSortableField


class IUserRepository:
    async def get_by_id(self, user_id: UUID) -> User | None: ...
    async def get_by_login(self, login: str) -> User | None: ...
    async def create(self, user: User) -> User: ...
    async def update(self, user: User) -> User: ...
    async def delete(self, user_id: UUID) -> bool: ...
    async def get_users(
            self,
            pagination_and_sorting: PaginationAndSorting[UserSortableField],
            department_member_filters: UserFilters = UserFilters()
    ) -> list[User]: ...
    async def count_users(
            self,
            department_member_filters: UserFilters = UserFilters()
    ) -> int: ...
    async def get_user_parents(
            self, user_id: UUID,
            pagination_and_sorting: PaginationAndSorting[UserSortableField],
            department_member_filters: UserFilters = UserFilters()
    ) -> list[User]: ...
    async def count_user_parents(
            self, user_id: UUID,
            department_member_filters: UserFilters = UserFilters()
    ) -> int: ...
    async def update_user_parents(
            self, user_id: UUID,
            ids_to_add: list[UUID],
            ids_to_delete: list[UUID]
    ) -> None: ...
    async def get_user_children(
            self, user_id: UUID,
            pagination_and_sorting: PaginationAndSorting[UserSortableField],
            department_member_filters: UserFilters = UserFilters()
    ) -> list[User]: ...
    async def count_user_children(
            self, user_id: UUID,
            department_member_filters: UserFilters = UserFilters()
    ) -> int: ...
    async def update_user_children(
            self, user_id: UUID,
            ids_to_add: list[UUID],
            ids_to_delete: list[UUID]
    ) -> None: ...

class IDepartmentRepository:
    async def get_department_members(
            self, department: Department,
            pagination_and_sorting: PaginationAndSorting[DepartmentMemberSortableField],
            department_member_filters: DepartmentMemberFilters = DepartmentMemberFilters()
    ) -> list[DepartmentMember]: ...
    async def count_department_members(
            self, department: Department,
            department_member_filters: DepartmentMemberFilters = DepartmentMemberFilters()
    ) -> list[DepartmentMember]: ...
    async def get_department_member(
            self,
            department: Department,
            user_id: UUID
    ) -> DepartmentMember: ...
    async def update_department_member(
            self, 
            department: Department,
            user_id: UUID, 
            position: DepartmentMemberPosition
    ) -> None: ...
