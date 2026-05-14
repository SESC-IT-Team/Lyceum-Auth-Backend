"""department

Revision ID: 00c739a834c0
Revises: c2adedc08506
Create Date: 2026-05-14 21:20:40.575019

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00c739a834c0'
down_revision: Union[str, Sequence[str], None] = 'c2adedc08506'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаём ENUM-тип перед добавлением колонки
    department_enum = sa.Enum(
        'academic_department',
        'olympiad_support_department',
        'medical_station',
        'educational_department',
        'library',
        'it_department',
        'laboratory_of_tech_teaching_aids',
        'competitive_selection_department',
        'additional_education_department',
        'dormitory',
        name='department',
        create_type=False  # Важно: не создавать автоматически, сделаем это вручную
    )

    # Явно создаём тип в БД
    department_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('users', sa.Column('department', department_enum, nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'department')

    # Удаляем ENUM-тип после удаления колонки
    department_enum = sa.Enum(
        'academic_department',
        'olympiad_support_department',
        'medical_station',
        'educational_department',
        'library',
        'it_department',
        'laboratory_of_tech_teaching_aids',
        'competitive_selection_department',
        'additional_education_department',
        'dormitory',
        name='department',
        create_type=False
    )
    department_enum.drop(op.get_bind(), checkfirst=True)