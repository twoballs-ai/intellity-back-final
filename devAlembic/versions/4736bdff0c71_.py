"""empty message

Revision ID: 4736bdff0c71
Revises: 4e1a5eb7aa18
Create Date: 2024-06-03 13:39:45.226797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4736bdff0c71'
down_revision: Union[str, None] = '4e1a5eb7aa18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chapter_model', sa.Column('total_modules_in_chapter', sa.BigInteger(), nullable=True))
    op.add_column('chapter_model', sa.Column('total_stages_in_chapter', sa.BigInteger(), nullable=True))
    op.add_column('course_model', sa.Column('total_chapters', sa.BigInteger(), nullable=True))
    op.add_column('course_model', sa.Column('total_modules', sa.BigInteger(), nullable=True))
    op.add_column('course_model', sa.Column('total_stages', sa.BigInteger(), nullable=True))
    op.add_column('module_model', sa.Column('total_stages_in_module', sa.BigInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('module_model', 'total_stages_in_module')
    op.drop_column('course_model', 'total_stages')
    op.drop_column('course_model', 'total_modules')
    op.drop_column('course_model', 'total_chapters')
    op.drop_column('chapter_model', 'total_stages_in_chapter')
    op.drop_column('chapter_model', 'total_modules_in_chapter')
    # ### end Alembic commands ###
