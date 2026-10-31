"""0002_add_auth_user_id_to_users

Add auth_user_id column and unique index to users table for stable Supabase Auth UUID mapping.

Revision ID: 0002_add_auth_user_id_to_users
Revises: 0001_initial_mandap_schema
Create Date: 2026-10-31
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0002_add_auth_user_id_to_users'
down_revision: Union[str, Sequence[str], None] = '0001_initial_mandap_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('auth_user_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_auth_user_id'), 'users', ['auth_user_id'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_users_auth_user_id'), table_name='users')
    op.drop_column('users', 'auth_user_id')
