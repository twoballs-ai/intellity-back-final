"""empty message

Revision ID: e29324e64d33
Revises: ca699a9d0f17
Create Date: 2024-06-20 12:25:06.254548

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e29324e64d33'
down_revision: Union[str, None] = 'ca699a9d0f17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blog_category_model',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_index(op.f('ix_blog_category_model_id'), 'blog_category_model', ['id'], unique=False)
    op.create_table('blog_model',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=30), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['blog_category_model.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['user_model.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_model_id'), 'blog_model', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_blog_model_id'), table_name='blog_model')
    op.drop_table('blog_model')
    op.drop_index(op.f('ix_blog_category_model_id'), table_name='blog_category_model')
    op.drop_table('blog_category_model')
    # ### end Alembic commands ###
