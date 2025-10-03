"""add firebase auth fields

Revision ID: 27fef969e039
Revises: 
Create Date: 2025-10-03 12:35:39.308546+02:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27fef969e039'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns
    op.add_column('users', sa.Column('firebase_uid', sa.String(), nullable=True))
    op.add_column('users', sa.Column('auth_provider', sa.String(), server_default='email', nullable=False))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), server_default='false', nullable=False))
    
    # Create unique index on firebase_uid
    op.create_index('ix_users_firebase_uid', 'users', ['firebase_uid'], unique=True)
    
    # Make hashed_password nullable
    op.alter_column('users', 'hashed_password', nullable=True)

def downgrade():
    op.drop_index('ix_users_firebase_uid', table_name='users')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'auth_provider')
    op.drop_column('users', 'firebase_uid')
    op.alter_column('users', 'hashed_password', nullable=False)

