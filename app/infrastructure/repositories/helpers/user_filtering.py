from app.domain.entities.user_filters import UserFilters
from sqlalchemy.orm.util import AliasedClass
from app.infrastructure.models import UserModel
from sqlalchemy.sql.selectable import Select

def apply_user_filters_to_query[T: Select](
        query: T,
        alias: type[UserModel] | AliasedClass[UserModel] = UserModel,
        user_filters: UserFilters = UserFilters()
) -> T:
    if user_filters.ids:
        query = query.where(alias.id.in_(user_filters.ids))
    if user_filters.search:
        pattern = f'%{user_filters.search}%'
        query = query.where(alias.login.ilike(pattern) |
                            alias.first_name.ilike(pattern) |
                            alias.middle_name.ilike(pattern) |
                            alias.last_name.ilike(pattern) |
                            alias.full_name.ilike(pattern))
    if user_filters.gender:
        query = query.where(alias.gender == user_filters.gender)
    if user_filters.roles:
        query = query.where(alias.roles.overlap(user_filters.roles))
    if user_filters.grades:
        query = query.where(alias.grade.in_(user_filters.grades))
    if user_filters.letters:
        query = query.where(alias.letter.in_(user_filters.letters))
    if user_filters.graduation_years:
        query = query.where(alias.graduation_year.in_(user_filters.graduation_years))
    if user_filters.class_names:
        query = query.where(alias.class_name.in_(user_filters.class_names))
    if user_filters.lives_in_dormitory is not None:
        query = query.where(alias.lives_in_dormitory == user_filters.lives_in_dormitory)
    return query