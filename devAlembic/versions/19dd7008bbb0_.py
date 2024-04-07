"""empty message

Revision ID: 19dd7008bbb0
Revises: 73ecd6d0aa7f
Create Date: 2024-03-25 00:53:16.683615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19dd7008bbb0'
down_revision: Union[str, None] = '73ecd6d0aa7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stage_model', sa.Column('title', sa.String(length=30), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stage_model', 'title')
    # ### end Alembic commands ###
