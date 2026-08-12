from sesc_auth_sdk.enums import Role
from sesc_auth_sdk.enums import Gender
from uuid import UUID
from sqlalchemy.orm.util import AliasedClass
from app.infrastructure.models import UserModel
from sqlalchemy.sql.selectable import Select

def apply_user_filters_to_query(query: Select, alias: type[UserModel] | AliasedClass[UserModel] = UserModel,
                                ids: list[UUID] | None = None, search: str | None = None,
                                gender: Gender | None = None, roles: list[Role] | None = None,
                                grades: list[int] | None = None, letters: list[str] | None = None,
                                graduation_years: list[int] | None = None,
                                class_names: list[str] | None = None,
                                lives_in_dormitory: bool | None = None):
    if ids:
        query = query.where(alias.id.in_(ids))
    if search:
        pattern = f'%{search}%'
        query = query.where(alias.login.ilike(pattern) |
                            alias.first_name.ilike(pattern) |
                            alias.middle_name.ilike(pattern) |
                            alias.last_name.ilike(pattern) |
                            alias.full_name.ilike(pattern))
    if gender:
        query = query.where(alias.gender == gender)
    if roles:
        query = query.where(alias.roles.overlap(roles))
    if grades:
        query = query.where(alias.grade.in_(grades))
    if letters:
        query = query.where(alias.letter.in_(letters))
    if graduation_years:
        query = query.where(alias.graduation_year.in_(graduation_years))
    if class_names:
        query = query.where(alias.class_name.in_(class_names))
    if lives_in_dormitory is not None:
        query = query.where(alias.lives_in_dormitory == lives_in_dormitory)
    return query