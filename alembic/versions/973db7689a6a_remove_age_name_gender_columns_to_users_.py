"""Remove age, name, gender columns to users table

Revision ID: 973db7689a6a
Revises: ace916110383
Create Date: 2025-05-25 23:30:00.613099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '973db7689a6a'
down_revision: Union[str, None] = 'ace916110383'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'age')
    op.drop_column('user', 'name')
    op.drop_column('user', 'gender')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('gender', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###