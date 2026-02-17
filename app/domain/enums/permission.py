from enum import Enum

from app.domain.enums.role import Role


class Permission(str, Enum):
    users_create = "users:create"
    users_read = "users:read"
    users_update = "users:update"
    users_delete = "users:delete"
    auth_login = "auth:login"
    auth_logout = "auth:logout"
    auth_verify = "auth:verify"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.admin: {
        Permission.users_create,
        Permission.users_read,
        Permission.users_update,
        Permission.users_delete,
        Permission.auth_login,
        Permission.auth_logout,
        Permission.auth_verify,
    },
    Role.teacher: {
        Permission.auth_login,
        Permission.auth_logout,
        Permission.auth_verify,
    },
    Role.student: {
        Permission.auth_login,
        Permission.auth_logout,
        Permission.auth_verify,
    },
    Role.staff: {
        Permission.auth_login,
        Permission.auth_logout,
        Permission.auth_verify,
    },
}


def get_permissions_for_role(role: Role) -> set[Permission]:
    return ROLE_PERMISSIONS.get(role, set())
