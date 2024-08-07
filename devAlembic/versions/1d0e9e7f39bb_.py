"""empty message

Revision ID: 1d0e9e7f39bb
Revises: 6274d86a4e4b
Create Date: 2024-08-02 12:23:54.928384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d0e9e7f39bb'
down_revision: Union[str, None] = '6274d86a4e4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('log_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_log_types_id'), 'log_types', ['id'], unique=False)
    op.create_index(op.f('ix_log_types_name'), 'log_types', ['name'], unique=True)
    op.add_column('action_logs', sa.Column('log_type_id', sa.Integer(), nullable=True))
    op.add_column('action_logs', sa.Column('object_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_action_logs_object_id'), 'action_logs', ['object_id'], unique=False)
    op.create_foreign_key(None, 'action_logs', 'log_types', ['log_type_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'action_logs', type_='foreignkey')
    op.drop_index(op.f('ix_action_logs_object_id'), table_name='action_logs')
    op.drop_column('action_logs', 'object_id')
    op.drop_column('action_logs', 'log_type_id')
    op.drop_index(op.f('ix_log_types_name'), table_name='log_types')
    op.drop_index(op.f('ix_log_types_id'), table_name='log_types')
    op.drop_table('log_types')
    # ### end Alembic commands ###
