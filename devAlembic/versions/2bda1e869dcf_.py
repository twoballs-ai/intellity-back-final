"""empty message

Revision ID: 2bda1e869dcf
Revises: 89aa5c7ae544
Create Date: 2024-04-23 22:47:35.343815

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bda1e869dcf'
down_revision: Union[str, None] = '89aa5c7ae544'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_model', 'is_teacher')
    op.drop_column('user_model', 'is_student')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_model', sa.Column('is_student', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('user_model', sa.Column('is_teacher', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
