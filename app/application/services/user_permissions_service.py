from app.domain.entities.user import User
from app.domain.enums.permission import Permissions, PermissionType, MASTER_PERMISSIONS, \
    SUPER_PERMISSIONS, ABSOLUTE_PERMISSIONS, BASIC_PERMISSIONS


class UserPermissionsService:
    @staticmethod
    def can_update_user(actor: User, target: User) -> bool:
        if actor.is_allowed(Permissions.Auth.SuperPermission.grant) or actor.is_allowed(Permissions.Auth.SuperPermission.revoke):
            return True
        if actor.is_allowed(Permissions.Auth.MasterPermissions.write) and not target.is_allowed(Permissions.Auth.MasterPermissions.write):
            return True
        if actor.is_allowed(Permissions.Auth.BasicPermissions.write) and not target.is_allowed(Permissions.Auth.BasicPermissions.write):
            return True
        return False

    @staticmethod
    def are_permissions_valid(perms: list[PermissionType]) -> bool:
        given = set(perms)
        if any(p in given for p in MASTER_PERMISSIONS):
            missing = BASIC_PERMISSIONS - given
            if missing:
                return False
        if any(p in given for p in SUPER_PERMISSIONS):
            missing = MASTER_PERMISSIONS - given
            if missing:
                return False
        if any(p in given for p in ABSOLUTE_PERMISSIONS):
            missing = SUPER_PERMISSIONS - given
            if missing:
                return False
        return True


    @staticmethod
    def is_update_allowed(actor: User, target: User, new_permissions: list[PermissionType]) -> bool:
        if not UserPermissionsService.are_permissions_valid(new_permissions):
            return False
        revoked: list[PermissionType] = [p for p in target.permissions if p not in new_permissions]
        granted: list[PermissionType] = [p for p in new_permissions if p not in target.permissions]
        for p in revoked:
            if p in BASIC_PERMISSIONS and not actor.is_allowed(Permissions.Auth.BasicPermissions.write):
                return False
            if p in MASTER_PERMISSIONS and not actor.is_allowed(Permissions.Auth.MasterPermissions.write):
                return False
            if p in SUPER_PERMISSIONS and not actor.is_allowed(Permissions.Auth.SuperPermission.revoke):
                return False
            if p in ABSOLUTE_PERMISSIONS:
                return False
        for p in granted:
            if p in BASIC_PERMISSIONS and not actor.is_allowed(Permissions.Auth.BasicPermissions.write):
                return False
            if p in MASTER_PERMISSIONS and not actor.is_allowed(Permissions.Auth.MasterPermissions.write):
                return False
            if p in SUPER_PERMISSIONS and not actor.is_allowed(Permissions.Auth.SuperPermission.grant):
                return False
            if p in ABSOLUTE_PERMISSIONS:
                return False
        return True