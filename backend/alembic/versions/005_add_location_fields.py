"""Add location and character fields to line detections

Revision ID: 005_add_location_fields
Revises: 004_add_line_detections
Create Date: 2025-11-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '005_add_location_fields'
down_revision: Union[str, None] = '004_add_line_detections'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('line_detections', sa.Column('page_number', sa.Integer(), nullable=True))
    op.add_column('line_detections', sa.Column('character', sa.String(length=100), nullable=True))
    op.add_column('line_detections', sa.Column('scene_number', sa.Integer(), nullable=True))
    op.add_column('line_detections', sa.Column('scene_heading', sa.String(length=500), nullable=True))
    op.add_column('line_detections', sa.Column('timing_estimate', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('line_detections', 'timing_estimate')
    op.drop_column('line_detections', 'scene_heading')
    op.drop_column('line_detections', 'scene_number')
    op.drop_column('line_detections', 'character')
    op.drop_column('line_detections', 'page_number')
