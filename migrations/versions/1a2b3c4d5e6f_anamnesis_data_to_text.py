"""
Change anamneses.data column from JSONB to TEXT (store JSON as string)

Revision ID: 1a2b3c4d5e6f
Revises: 7c7d50333c3f
Create Date: 2025-09-22
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "1a2b3c4d5e6f"
down_revision = "7c7d50333c3f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert JSONB to TEXT string
    op.execute("ALTER TABLE anamneses ALTER COLUMN data TYPE TEXT USING data::text")


def downgrade() -> None:
    # Convert back TEXT to JSONB
    op.execute("ALTER TABLE anamneses ALTER COLUMN data TYPE JSONB USING data::jsonb")

