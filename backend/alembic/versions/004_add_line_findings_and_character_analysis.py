"""Add line findings and character analysis tables

Revision ID: 004
Revises: 003
Create Date: 2025-01-16 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "line_findings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("script_id", sa.Integer(), nullable=False),
        sa.Column("scene_id", sa.Integer(), nullable=True),
        sa.Column("line_start", sa.Integer(), nullable=False),
        sa.Column("line_end", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.Float(), nullable=False),
        sa.Column("matched_text", sa.Text(), nullable=False),
        sa.Column("context_before", sa.Text(), nullable=True),
        sa.Column("context_after", sa.Text(), nullable=True),
        sa.Column("match_count", sa.Integer(), nullable=False),
        sa.Column("rating_impact", sa.String(length=10), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["script_id"], ["scripts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_line_findings_id"), "line_findings", ["id"], unique=False)

    op.create_table(
        "character_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("script_id", sa.Integer(), nullable=False),
        sa.Column("character_name", sa.String(length=255), nullable=False),
        sa.Column("profanity_count", sa.Integer(), nullable=False),
        sa.Column("violence_scenes", sa.Integer(), nullable=False),
        sa.Column("sex_scenes", sa.Integer(), nullable=False),
        sa.Column("drug_scenes", sa.Integer(), nullable=False),
        sa.Column("total_problematic_scenes", sa.Integer(), nullable=False),
        sa.Column("severity_score", sa.Float(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=True),
        sa.Column("scene_appearances", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["script_id"], ["scripts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_character_analyses_id"), "character_analyses", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_character_analyses_id"), table_name="character_analyses")
    op.drop_table("character_analyses")
    op.drop_index(op.f("ix_line_findings_id"), table_name="line_findings")
    op.drop_table("line_findings")
