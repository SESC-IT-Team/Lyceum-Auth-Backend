"""spravki permissions

Revision ID: 4e576c92343a
Revises: 0bbb5d95f081
Create Date: 2026-05-10 21:01:47.153145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import lambdas

# revision identifiers, used by Alembic.
revision: str = '4e576c92343a'
down_revision: Union[str, Sequence[str], None] = '0bbb5d95f081'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ENUM_NAME = 'permissiontype'

NEW_VALUES = (
    'spravki_orders_create',
    'spravki_orders_get_my',
    'spravki_orders_get',
)

OLD_VALUES = (
    'auth_users_create',
    'auth_users_read',
    'auth_users_update',
    'auth_users_delete',

    'auth_permissions_presets_create',
    'auth_permissions_presets_read',
    'auth_permissions_presets_update',
    'auth_permissions_presets_delete',

    'auth_basic_permissions_write',

    'auth_keys_revoke',

    'auth_master_permissions_write',

    'auth_super_permission_grant',
    'auth_super_permission_revoke',

    'technical_support_orders_create',
    'technical_support_orders_set_department',
    'technical_support_orders_get',
    'technical_support_orders_set_status',
    'technical_support_orders_set_worker'
)


def upgrade() -> None:
    """Upgrade schema."""
    for value in NEW_VALUES:
        op.execute(
            f"ALTER TYPE {ENUM_NAME} ADD VALUE IF NOT EXISTS '{value}';"
        )



def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f"ALTER TYPE {ENUM_NAME} RENAME TO {ENUM_NAME}_old;")
    joiner = ',\n'
    op.execute(
        f"""
            CREATE TYPE {ENUM_NAME} AS ENUM (
                {joiner.join(map(lambda val: f"'{val}'", OLD_VALUES))}
            );
            """
    )

    op.execute(
        f"""
                ALTER TABLE users
                ALTER COLUMN permissions
                TYPE {ENUM_NAME}[]
                USING permissions::text[]::{ENUM_NAME}[]
                """
    )

    op.execute(
        f"""
                ALTER TABLE permissions_presets
                ALTER COLUMN permissions
                TYPE {ENUM_NAME}[]
                USING permissions::text[]::{ENUM_NAME}[]
                """
    )
    op.execute(f"DROP TYPE {ENUM_NAME}_old;")
