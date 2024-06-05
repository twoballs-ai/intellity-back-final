"""empty message

Revision ID: f50d4a9f8338
Revises: d680976d29da
Create Date: 2024-05-31 23:49:23.122464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f50d4a9f8338'
down_revision: Union[str, None] = 'd680976d29da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course_model', sa.Column('cover_image_name', sa.String(), nullable=True))
    op.add_column('course_model', sa.Column('cover_path', sa.String(), nullable=True))
    op.create_index(op.f('ix_course_model_cover_image_name'), 'course_model', ['cover_image_name'], unique=False)
    op.create_unique_constraint(None, 'course_model', ['cover_path'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'course_model', type_='unique')
    op.drop_index(op.f('ix_course_model_cover_image_name'), table_name='course_model')
    op.drop_column('course_model', 'cover_path')
    op.drop_column('course_model', 'cover_image_name')
    # ### end Alembic commands ###
