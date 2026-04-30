from enum import Enum


class Permission(str, Enum):
    # auth service
    auth_users_create = "auth:users:create"
    auth_users_read = "auth:users:read"
    auth_users_update = "auth:users:update"
    auth_users_delete = "auth:users:delete"

    # technical support service
    technical_support_orders_create = "technical_support:orders:create"
    technical_support_orders_set_department = "technical_support:orders:set_department"
    technical_support_orders_get = "technical_support:orders:get"
    technical_support_orders_set_status = "technical_support:orders:set_status"
    technical_support_orders_set_worker = "technical_support:orders:set_worker"


class Permissions:
    class Auth:
        class Users:
            create = Permission.auth_users_create
            read = Permission.auth_users_read
            update = Permission.auth_users_update
            delete = Permission.auth_users_delete

    class TechnicalSupport:
        class Orders:
            create = Permission.technical_support_orders_create
            set_department = Permission.technical_support_orders_set_department
            get = Permission.technical_support_orders_get
            set_status = Permission.technical_support_orders_set_status
            set_worker = Permission.technical_support_orders_set_worker
