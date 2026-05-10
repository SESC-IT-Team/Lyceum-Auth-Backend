"""parent guest and graduate roles

Revision ID: 0bbb5d95f081
Revises: bad0fead8832
Create Date: 2026-05-10 15:24:45.663598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0bbb5d95f081'
down_revision: Union[str, Sequence[str], None] = 'bad0fead8832'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ENUM_NAME = 'role'

NEW_VALUES = {
    'parent',
    'guest',
    'graduate'
}

roles_enum = postgresql.ENUM(
    'admin', 'teacher', 'student', 'staff', 'parent', 'guest', 'graduate',
    name=ENUM_NAME,
    create_type=False
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

    op.execute(
        f"""
            CREATE TYPE {ENUM_NAME} AS ENUM (
                'admin',
                'teacher', 
                'student', 
                'staff'
            );
            """
    )

    op.execute(
        f"""
                ALTER TABLE users
                ALTER COLUMN roles
                TYPE {ENUM_NAME}[]
                USING roles::text[]::role[]
                """
    )

    op.execute(f"DROP TYPE {ENUM_NAME}_old;")
