from app.domain.entities.user_filters import UserFilters
from app.domain.entities.pagination_and_sorting import PaginationAndSorting
from copy import deepcopy
from datetime import date
from uuid import UUID, uuid4
import logging

from fastapi import HTTPException, status

from app.application.services.authentik_service import AuthentikService
from app.domain.entities.user import User
from sesc_auth_sdk.enums.gender import Gender
from sesc_auth_sdk.enums.role import Role
from app.application.interfaces.repositories import IUserRepository
from app.domain.enums.sorting_order import SortingOrder
from app.domain.enums.user_sortable_field import UserSortableField
from sesc_openfga_sdk.lyceum_openfga_service import LyceumOpenFGAService

from sesc_openfga_sdk.models import Student as OpenFGAStudent, User as OpenFGAUser

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self, 
        user_repository: IUserRepository,
        authentik_service: AuthentikService
    ):
        self._repo = user_repository
        self._auth_service = authentik_service

    async def check_user_exists_by_id_or_raise(self, user_id: UUID) -> None:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    async def check_login_not_occupied_or_raise(self, login: str) -> None:
        user = await self._repo.get_by_login(login)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login already occupied",
            )

    async def get_user_by_id(self, user_id: UUID) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        return user

    async def create(
        self,
        last_name: str,
        first_name: str,
        login: str,
        roles: list[Role],
        gender: Gender,
        lives_in_dormitory: bool,
        birthday: date | None = None,
        middle_name: str | None = None,
        grade: int | None = None,
        letter: str | None = None,
        graduation_year: int | None = None
    ) -> User:
        user = User(
            id=uuid4(),
            pk=0,
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            login=login,
            roles=roles,
            birthday=birthday,
            gender=gender,
            grade=grade,
            letter=letter,
            graduation_year=graduation_year,
            lives_in_dormitory=lives_in_dormitory
        )
        await self.check_login_not_occupied_or_raise(login)
        pk, created_uuid = await self._auth_service.create_user(user.login, user.full_name)
        try:
            user.pk = pk
            user.id = created_uuid
            created = await self._repo.create(user)
        except Exception as exc:
            logger.error(f"DB insert failed. Rolling back Authentik user pk={pk}: {exc}")
            try:
                await self._auth_service.delete_user(pk)
            except Exception as delete_exc:
                logger.error(f"Rollback of user creation failed pk={pk}: {delete_exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed",
            ) from exc
        logger.info(f"User created successfully: pk={created.pk}, user={created}")
        return created

    async def update_user(
        self,
        user_id: UUID,
        *,
        last_name: str | None = None,
        first_name: str | None = None,
        middle_name: str | None = None,
        roles: list[Role] | None = None,
        gender: Gender | None = None,
        grade: int | None = None,
        letter: str | None = None,
        graduation_year: int | None = None,
        login: str | None = None,
        birthday: date | None = None,
        lives_in_dormitory: bool | None = None,
    ) -> User:
        old_user = await self.get_user_by_id(user_id)
        user = deepcopy(old_user)
        if login or first_name or middle_name or last_name:
            await self._auth_service.update_user_info(user.pk, login, user.full_name)
        if last_name:
            user.last_name = last_name
        if first_name:
            user.first_name = first_name
        if middle_name:
            user.middle_name = middle_name
        if roles:
            user.roles = roles
        if gender:
            user.gender = gender
        if grade:
            user.grade = grade
        if letter:
            user.letter = letter
        if graduation_year:
            user.graduation_year = graduation_year
        if login:
            user.login = login
        if birthday:
            user.birthday = birthday
        if lives_in_dormitory is not None:
            user.lives_in_dormitory = lives_in_dormitory
        updated = await self._repo.update(user)
        if first_name or last_name or middle_name or login:
            await self._auth_service.update_user_info(updated.pk, login, user.full_name)
        logger.info(f"User update successful user_id={user_id}")
        return updated

    async def delete(self, user_id: UUID) -> None:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        await self._auth_service.delete_user(user.pk)
        await self._repo.delete(user_id)
        logger.info(f"User deletion successful user_id={user_id}")

    async def update_password(self, user_id: UUID, password: str) -> None:
        user = await self.get_user_by_id(user_id)
        await self._auth_service.update_user_password(user.pk, password)
        logger.info(f"User password update successful user_id={user_id}")

    async def list_users(
            self,
            pagination_and_sorting: PaginationAndSorting[UserSortableField],
            user_filters: UserFilters = UserFilters()
    ) -> list[User]:
        return await self._repo.get_users(pagination_and_sorting, user_filters)

    async def count_users(
            self,
            user_filters: UserFilters = UserFilters()
    ) -> int:
        return await self._repo.count_users(user_filters)

    async def get_parents_by_child_id(
            self, user_id: UUID,
            pagination_and_sorting: PaginationAndSorting[UserSortableField],
            user_filters: UserFilters = UserFilters()
    ) -> list[User]:
        await self.check_user_exists_by_id_or_raise(user_id)
        parents = await self._repo.get_user_parents(
            user_id,
            pagination_and_sorting,
            user_filters
        )
        return parents

    async def count_parents_by_child_id(
            self, user_id: UUID,
            user_filters: UserFilters = UserFilters()
    ) -> int:
        await self.check_user_exists_by_id_or_raise(user_id)
        return await self._repo.count_user_parents(
            user_id,
            user_filters
        )

    async def update_parents_by_child_id(
            self, user_id: UUID,
            parent_ids_to_add: list[UUID] | None = None,
            parent_ids_to_delete: list[UUID] | None = None
    ) -> None:
        if parent_ids_to_add is None:
            parent_ids_to_add = []
        if parent_ids_to_delete is None:
            parent_ids_to_delete = []
        if user_id in parent_ids_to_add or user_id in parent_ids_to_delete:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User cannot be parent of themselves')
        await self.check_user_exists_by_id_or_raise(user_id)
        found_parents_to_delete_count = await self._repo.count_user_parents(user_id, UserFilters(ids=parent_ids_to_delete))
        found_parents_to_add_count = await self._repo.count_user_parents(user_id, UserFilters(ids=parent_ids_to_add))
        if found_parents_to_add_count > 0 or found_parents_to_delete_count != len(parent_ids_to_delete):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Some parents already added or already deleted')
        await self._repo.update_user_parents(user_id, parent_ids_to_add, parent_ids_to_delete)
        logger.info(f"User parents update successful user_id={user_id}")

    async def get_children_by_parent_id(
            self, user_id: UUID,
            pagination_and_sorting: PaginationAndSorting[UserSortableField],
            user_filters: UserFilters = UserFilters()
    ) -> list[User]:
        await self.check_user_exists_by_id_or_raise(user_id)
        parents = await self._repo.get_user_children(
            user_id,
            pagination_and_sorting,
            user_filters
        )
        return parents

    async def count_children_by_parent_id(
            self, user_id: UUID,
            user_filters: UserFilters = UserFilters()
    ) -> int:
        await self.check_user_exists_by_id_or_raise(user_id)
        return await self._repo.count_user_children(
            user_id,
            user_filters
        )

    async def update_children_by_parent_id(
            self, user_id: UUID,
            child_ids_to_add: list[UUID] | None = None,
            child_ids_to_delete: list[UUID] | None = None
    ) -> None:
        if child_ids_to_add is None:
            child_ids_to_add = []
        if child_ids_to_delete is None:
            child_ids_to_delete = []
        if user_id in child_ids_to_add or user_id in child_ids_to_delete:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User cannot be child of themselves')
        await self.check_user_exists_by_id_or_raise(user_id)
        found_children_to_delete_count = await self._repo.count_user_children(user_id, UserFilters(ids=child_ids_to_delete))
        found_children_to_add_count = await self._repo.count_user_children(user_id, UserFilters(ids=child_ids_to_add))
        if found_children_to_add_count > 0 or found_children_to_delete_count != len(child_ids_to_delete):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Some children already added or already deleted')
        await self._repo.update_user_children(user_id, child_ids_to_add, child_ids_to_delete)
        logger.info(f"User children update successful user_id={user_id}")

    async def get_child_of_parent(self, child_id: UUID, parent_id: UUID) -> User:
        await self.check_user_exists_by_id_or_raise(parent_id)

        return await self.get_user_by_id(child_id)
