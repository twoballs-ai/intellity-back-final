"""empty message

Revision ID: df413416b516
Revises: b60897b836d8
Create Date: 2024-06-19 21:32:34.530054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df413416b516'
down_revision: Union[str, None] = 'b60897b836d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('privilege_model',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_privilege_model_id'), 'privilege_model', ['id'], unique=False)
    op.create_table('role_model',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_role_model_id'), 'role_model', ['id'], unique=False)
    op.create_table('role_privilege_association',
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('privilege_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['privilege_id'], ['privilege_model.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['role_model.id'], )
    )
    op.create_table('site_user_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['user_model.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admin_role_association',
    sa.Column('site_user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role_model.id'], ),
    sa.ForeignKeyConstraint(['site_user_id'], ['site_user_model.id'], )
    )
    op.add_column('user_model', sa.Column('is_active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_model', 'is_active')
    op.drop_table('admin_role_association')
    op.drop_table('site_user_model')
    op.drop_table('role_privilege_association')
    op.drop_index(op.f('ix_role_model_id'), table_name='role_model')
    op.drop_table('role_model')
    op.drop_index(op.f('ix_privilege_model_id'), table_name='privilege_model')
    op.drop_table('privilege_model')
    # ### end Alembic commands ###
