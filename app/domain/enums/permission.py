from enum import Enum


class PermissionType(str, Enum):
    # auth service
    auth_users_create = "auth:users:create"
    auth_users_read = "auth:users:read"
    auth_users_update = "auth:users:update"
    auth_users_delete = "auth:users:delete"

    auth_basic_permissions_write = "auth:basic_permissions:write"
    auth_keys_revoke = "auth:keys:revoke"

    auth_master_permissions_write = "auth:master_permissions:write"

    auth_super_permission_grant = "auth:super_permission:grant"
    auth_super_permission_revoke = "auth:super_permission:revoke"


    # technical support service
    technical_support_orders_create = "technical_support:orders:create"
    technical_support_orders_set_department = "technical_support:orders:set_department"
    technical_support_orders_get = "technical_support:orders:get"
    technical_support_orders_set_status = "technical_support:orders:set_status"
    technical_support_orders_set_worker = "technical_support:orders:set_worker"


class Permissions:
    class Auth:
        class Users:
            create = PermissionType.auth_users_create
            read = PermissionType.auth_users_read
            update = PermissionType.auth_users_update
            delete = PermissionType.auth_users_delete

        class BasicPermissions:
            write = PermissionType.auth_basic_permissions_write

        class Keys:
            revoke = PermissionType.auth_keys_revoke

        class MasterPermissions:
            write = PermissionType.auth_master_permissions_write

        class SuperPermission:
            grant = PermissionType.auth_super_permission_grant
            revoke = PermissionType.auth_super_permission_revoke

    class TechnicalSupport:
        class Orders:
            create = PermissionType.technical_support_orders_create
            set_department = PermissionType.technical_support_orders_set_department
            get = PermissionType.technical_support_orders_get
            set_status = PermissionType.technical_support_orders_set_status
            set_worker = PermissionType.technical_support_orders_set_worker

ALL_PERMISSIONS: set[PermissionType] = {p for p in PermissionType}

ABSOLUTE_PERMISSIONS: set[PermissionType] = {
    Permissions.Auth.SuperPermission.grant,
    Permissions.Auth.SuperPermission.revoke,
}

SUPER_PERMISSIONS: set[PermissionType] = {
    Permissions.Auth.MasterPermissions.write,
}

MASTER_PERMISSIONS: set[PermissionType] = {
    Permissions.Auth.BasicPermissions.write,
    Permissions.Auth.Keys.revoke
}

BASIC_PERMISSIONS: set[PermissionType] = ALL_PERMISSIONS - MASTER_PERMISSIONS - SUPER_PERMISSIONS - ABSOLUTE_PERMISSIONS
