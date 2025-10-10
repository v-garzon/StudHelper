"""add class and document descriptions

Revision ID: add document descriptions
Revises: refactor_user_model
Create Date: 2025-10-10 11:45:00.000000

"""
from alembic import op
import sqlalchemy as sauvive


# revision identifiers, used by Alembic.
revision = 'add_document_descriptions'
down_revision = 'refactor_user_model'  # Replace with your last migration ID
branch_labels = None
depends_on = None


def upgrade():
    # Add description to documents table
    op.add_column('documents', sa.Column('description', sa.Text(), nullable=True))
    
    # Add url field for YouTube videos
    op.add_column('documents', sa.Column('url', sa.Text(), nullable=True))
    
    # Add indexes for better query performance
    op.create_index('idx_documents_class_id', 'documents', ['class_id'])
    op.create_index('idx_documents_session_id', 'documents', ['session_id'])


def downgrade():
    # Remove indexes
    op.drop_index('idx_documents_session_id', table_name='documents')
    op.drop_index('idx_documents_class_id', table_name='documents')
    
    # Remove columns
    op.drop_column('documents', 'url')
    op.drop_column('documents', 'description')


