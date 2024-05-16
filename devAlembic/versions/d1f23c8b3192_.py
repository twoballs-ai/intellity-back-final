"""empty message

Revision ID: d1f23c8b3192
Revises: b51d76045f36
Create Date: 2024-05-16 18:26:59.537890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1f23c8b3192'
down_revision: Union[str, None] = 'b51d76045f36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chapter_model', sa.Column('previous_chapter_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'chapter_model', 'chapter_model', ['previous_chapter_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'chapter_model', type_='foreignkey')
    op.drop_column('chapter_model', 'previous_chapter_id')
    # ### end Alembic commands ###
