"""update bio column

Revision ID: bce670700cbd
Revises: f386ca7da942
Create Date: 2026-03-26 18:50:11.852397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bce670700cbd'
down_revision = 'f386ca7da942'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE users SET bio = '' WHERE bio IS NULL")

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'bio',
            existing_type=sa.TEXT(),
            nullable=False,
            server_default=''
        )
    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'bio',
            existing_type=sa.TEXT(),
            nullable=True,
            server_default=None
        )

    # ### end Alembic commands ###
