"""empty message

Revision ID: 163287492934
Revises: df7d0071b5da
Create Date: 2024-09-25 15:56:14.464892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '163287492934'
down_revision: Union[str, None] = 'df7d0071b5da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stage_progress', sa.Column('is_locked', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stage_progress', 'is_locked')
    # ### end Alembic commands ###
