"""empty message

Revision ID: 583a7fd1e299
Revises: 9f7153863b56
Create Date: 2024-04-23 22:10:00.332810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '583a7fd1e299'
down_revision: Union[str, None] = '9f7153863b56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('teacher_model', 'age')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('teacher_model', sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
