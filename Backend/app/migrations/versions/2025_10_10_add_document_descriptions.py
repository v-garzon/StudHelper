"""add document descriptions

Revision ID: add_descriptions_001
Revises: refactor_user_model
Create Date: 2025-10-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_descriptions_001'
down_revision = 'refactor_user_model'
branch_labels = None
depends_on = None


def upgrade():
    
    # Add description to documents table
    op.add_column('documents', sa.Column('description', sa.Text(), nullable=True))
    
    # Add url field for YouTube videos
    op.add_column('documents', sa.Column('url', sa.Text(), nullable=True))
    
    # Add processing_status with default value
    op.add_column('documents', sa.Column('processing_status', sa.String(50), nullable=False, server_default='pending'))
    
    # Add processing_error
    op.add_column('documents', sa.Column('processing_error', sa.Text(), nullable=True))
    
    # Add indexes for better query performance
    op.create_index('idx_documents_class_id', 'documents', ['class_id'], unique=False)
    op.create_index('idx_documents_session_id', 'documents', ['session_id'], unique=False)


def downgrade():
    # Remove indexes
    op.drop_index('idx_documents_session_id', table_name='documents')
    op.drop_index('idx_documents_class_id', table_name='documents')
    
    # Remove columns
    op.drop_column('documents', 'processing_error')
    op.drop_column('documents', 'processing_status')
    op.drop_column('documents', 'url')
    op.drop_column('documents', 'description')
    op.drop_column('classes', 'description')