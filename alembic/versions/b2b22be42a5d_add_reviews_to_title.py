"""add reviews to Title

Revision ID: b2b22be42a5d
Revises: ba41a5957e10
Create Date: 2024-10-03 18:22:31.073136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b2b22be42a5d'
down_revision: Union[str, None] = 'ba41a5957e10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_reviews_title_id',
            'titles',
            ['title_id'],
            ['id'],
        )


def downgrade() -> None:
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.drop_constraint('fk_reviews_title_id', type_='foreignkey')
        batch_op.drop_column('title_id')
