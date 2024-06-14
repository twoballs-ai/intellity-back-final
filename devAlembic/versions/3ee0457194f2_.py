"""empty message

Revision ID: 3ee0457194f2
Revises: eeea31972b42
Create Date: 2024-06-13 09:53:27.649135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ee0457194f2'
down_revision: Union[str, None] = 'eeea31972b42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course_moderation_status_model',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('status')
    )
    op.create_index(op.f('ix_course_moderation_status_model_id'), 'course_moderation_status_model', ['id'], unique=False)
    op.add_column('course_model', sa.Column('moderation_status_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'course_model', 'course_moderation_status_model', ['moderation_status_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'course_model', type_='foreignkey')
    op.drop_column('course_model', 'moderation_status_id')
    op.drop_index(op.f('ix_course_moderation_status_model_id'), table_name='course_moderation_status_model')
    op.drop_table('course_moderation_status_model')
    # ### end Alembic commands ###