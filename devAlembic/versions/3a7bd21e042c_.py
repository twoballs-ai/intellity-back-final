"""empty message

Revision ID: 3a7bd21e042c
Revises: 880ba2800da3
Create Date: 2024-08-27 22:08:05.520610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a7bd21e042c'
down_revision: Union[str, None] = '880ba2800da3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('blog_category_model', 'title',
               existing_type=sa.VARCHAR(length=30),
               type_=sa.String(length=100),
               existing_nullable=True)
    op.add_column('course_enrollment', sa.Column('is_active', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('course_enrollment', 'is_active')
    op.alter_column('blog_category_model', 'title',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=30),
               existing_nullable=True)
    # ### end Alembic commands ###