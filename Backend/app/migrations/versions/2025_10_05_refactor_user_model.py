"""Refactor user model - remove username/full_name, add name/surname/alias

Revision ID: refactor_user_model
Revises: add_firebase_auth
Create Date: 2025-10-05

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'refactor_user_model'
down_revision = '27fef969e039'  # Replace with your actual previous revision
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns
    op.add_column('users', sa.Column('name', sa.String(), nullable=True))  # Nullable first for existing data
    op.add_column('users', sa.Column('surname', sa.String(), nullable=True))  # Nullable first for existing data
    op.add_column('users', sa.Column('alias', sa.String(), nullable=True))
    
    # Remove old columns (drop indexes first)
    op.drop_index('ix_users_username', table_name='users')
    op.drop_column('users', 'username')
    op.drop_column('users', 'full_name')
    
    # Make name and surname NOT NULL (since you deleted all users, this is safe)
    op.alter_column('users', 'name', nullable=False)
    op.alter_column('users', 'surname', nullable=False)

def downgrade():
    # Add back old columns
    op.add_column('users', sa.Column('username', sa.String(), nullable=False))
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    
    # Remove new columns
    op.drop_column('users', 'alias')
    op.drop_column('users', 'surname')
    op.drop_column('users', 'name')
    
    # Recreate username index
    op.create_index('ix_users_username', 'users', ['username'], unique=True)


