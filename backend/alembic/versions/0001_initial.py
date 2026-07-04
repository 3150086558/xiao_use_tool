"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-04 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    op.create_table(
        'records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('record_date', sa.Date(), nullable=False),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('sub_category', sa.String(length=50), server_default=''),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('account', sa.String(length=50), server_default=''),
        sa.Column('note', sa.String(length=500), server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('idx_records_user', 'records', ['user_id'])
    op.create_index('idx_records_date', 'records', ['record_date'])
    op.create_index('idx_records_user_date', 'records', ['user_id', 'record_date'])

    op.create_table(
        'menus',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('icon', sa.String(length=20), server_default=''),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('idx_menus_user', 'menus', ['user_id'])

    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('priority', sa.Integer(), server_default='0'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('idx_todos_user', 'todos', ['user_id'])

    op.create_table(
        'notes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('idx_notes_user', 'notes', ['user_id'])

    op.create_table(
        'db_connections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('db_type', sa.String(length=20), nullable=False),
        sa.Column('host', sa.String(length=100), server_default=''),
        sa.Column('port', sa.Integer(), server_default='0'),
        sa.Column('username', sa.String(length=100), server_default=''),
        sa.Column('password', sa.String(length=500), server_default=''),
        sa.Column('database', sa.String(length=100), server_default=''),
        sa.Column('sqlite_path', sa.String(length=500), server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('idx_db_conn_user', 'db_connections', ['user_id'])

    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=512), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('idx_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)
    op.create_index('idx_refresh_tokens_user', 'refresh_tokens', ['user_id'])


def downgrade() -> None:
    op.drop_index('idx_refresh_tokens_user', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_token', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    op.drop_index('idx_db_conn_user', table_name='db_connections')
    op.drop_table('db_connections')

    op.drop_index('idx_notes_user', table_name='notes')
    op.drop_table('notes')

    op.drop_index('idx_todos_user', table_name='todos')
    op.drop_table('todos')

    op.drop_index('idx_menus_user', table_name='menus')
    op.drop_table('menus')

    op.drop_index('idx_records_user_date', table_name='records')
    op.drop_index('idx_records_date', table_name='records')
    op.drop_index('idx_records_user', table_name='records')
    op.drop_table('records')

    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
