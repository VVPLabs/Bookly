"""init

Revision ID: 82096a464c87
Revises: 
Create Date: 2025-02-26 13:39:05.133047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel 


# revision identifiers, used by Alembic.
revision: str = '82096a464c87'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('book', 'published_date',
               existing_type=sa.VARCHAR(),
               type_=sa.Date(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('book', 'published_date',
               existing_type=sa.Date(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    # ### end Alembic commands ###
