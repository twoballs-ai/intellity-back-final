"""empty message

Revision ID: 434ba63d0c2c
Revises: 1d0e9e7f39bb
Create Date: 2024-08-02 12:57:15.308414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '434ba63d0c2c'
down_revision: Union[str, None] = '1d0e9e7f39bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('action_logs', sa.Column('model_name', sa.String(), nullable=True))
    op.create_index(op.f('ix_action_logs_model_name'), 'action_logs', ['model_name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_action_logs_model_name'), table_name='action_logs')
    op.drop_column('action_logs', 'model_name')
    # ### end Alembic commands ###