"""Add manual corrections table

Revision ID: 005
Revises: 004
Create Date: 2025-01-16 14:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "manual_corrections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("script_id", sa.Integer(), nullable=False),
        sa.Column("finding_id", sa.Integer(), nullable=True),
        sa.Column("scene_id", sa.Integer(), nullable=True),
        sa.Column("correction_type", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("severity", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("line_start", sa.Integer(), nullable=True),
        sa.Column("line_end", sa.Integer(), nullable=True),
        sa.Column("matched_text", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
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
        op.f("ix_manual_corrections_id"), "manual_corrections", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_manual_corrections_id"), table_name="manual_corrections")
    op.drop_table("manual_corrections")
