"""add manual corrections table

Revision ID: 004
Revises: 003
Create Date: 2025-01-16

"""
from alembic import op
import sqlalchemy as sa


revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'manual_corrections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=False),
        sa.Column('issue_id', sa.String(length=100), nullable=False),
        sa.Column('correction_type', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['script_id'], ['scripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_manual_corrections_id'), 'manual_corrections', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_manual_corrections_id'), table_name='manual_corrections')
    op.drop_table('manual_corrections')
