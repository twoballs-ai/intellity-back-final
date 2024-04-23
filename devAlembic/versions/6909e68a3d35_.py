"""empty message

Revision ID: 6909e68a3d35
Revises: 9c7985f435da
Create Date: 2024-04-13 23:59:43.655106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6909e68a3d35'
down_revision: Union[str, None] = '9c7985f435da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stage_items', sa.Column('name', sa.String(), nullable=True))
    op.add_column('stage_items', sa.Column('descriptions', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stage_items', 'descriptions')
    op.drop_column('stage_items', 'name')
    # ### end Alembic commands ###
