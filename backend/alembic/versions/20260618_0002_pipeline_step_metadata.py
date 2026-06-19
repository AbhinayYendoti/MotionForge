"""Ensure pipeline step metadata columns exist.

Revision ID: 20260618_0002
Revises: 20260618_0001
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260618_0002"
down_revision: Union[str, None] = "20260618_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    columns = _column_names("PipelineStep")
    if "errorMessage" not in columns:
        op.add_column("PipelineStep", sa.Column("errorMessage", sa.Text(), nullable=True))
    if "duration" not in columns:
        op.add_column("PipelineStep", sa.Column("duration", sa.Float(), nullable=True))


def downgrade() -> None:
    columns = _column_names("PipelineStep")
    if "duration" in columns:
        op.drop_column("PipelineStep", "duration")
    if "errorMessage" in columns:
        op.drop_column("PipelineStep", "errorMessage")
