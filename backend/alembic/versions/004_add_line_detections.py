"""Add line detections and user corrections

Revision ID: 004
Revises: 003
Create Date: 2025-11-16 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "line_detections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("script_id", sa.Integer(), nullable=False),
        sa.Column("scene_id", sa.Integer(), nullable=True),
        sa.Column("line_start", sa.Integer(), nullable=False),
        sa.Column("line_end", sa.Integer(), nullable=False),
        sa.Column("detected_text", sa.Text(), nullable=False),
        sa.Column("context_before", sa.Text(), nullable=True),
        sa.Column("context_after", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.Float(), nullable=False),
        sa.Column("parents_guide_severity", sa.String(length=20), nullable=True),
        sa.Column("character_name", sa.String(length=200), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("matched_patterns", sa.JSON(), nullable=True),
        sa.Column("is_false_positive", sa.Boolean(), nullable=False),
        sa.Column("user_corrected", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_line_detections_id"), "line_detections", ["id"], unique=False
    )

    op.create_table(
        "user_corrections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("script_id", sa.Integer(), nullable=False),
        sa.Column("detection_id", sa.Integer(), nullable=True),
        sa.Column("correction_type", sa.String(length=50), nullable=False),
        sa.Column("line_start", sa.Integer(), nullable=True),
        sa.Column("line_end", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("severity", sa.Float(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["detection_id"], ["line_detections.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_corrections_id"), "user_corrections", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_corrections_id"), table_name="user_corrections")
    op.drop_table("user_corrections")
    op.drop_index(op.f("ix_line_detections_id"), table_name="line_detections")
    op.drop_table("line_detections")
