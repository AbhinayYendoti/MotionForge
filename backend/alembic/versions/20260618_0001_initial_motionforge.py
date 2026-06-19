"""Initial MotionForge SQLAlchemy schema.

Revision ID: 20260618_0001
Revises:
Create Date: 2026-06-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260618_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


project_status = sa.Enum(
    "CREATED",
    "UPLOADED",
    "ANALYZING",
    "EXTRACTING",
    "STORYBOARDING",
    "PLANNING",
    "EVALUATING",
    "RENDERING",
    "COMPLETED",
    "FAILED",
    name="ProjectStatus",
)
render_status = sa.Enum("QUEUED", "RENDERING", "COMPLETED", "FAILED", name="RenderStatus")
pipeline_status = sa.Enum("PENDING", "RUNNING", "COMPLETED", "FAILED", name="PipelineStepStatus")


def upgrade() -> None:
    bind = op.get_bind()
    project_status.create(bind, checkfirst=True)
    render_status.create(bind, checkfirst=True)
    pipeline_status.create(bind, checkfirst=True)

    op.create_table(
        "User",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("clerkId", sa.String(), nullable=False, unique=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_table(
        "Project",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("userId", sa.String(), sa.ForeignKey("User.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("status", project_status, nullable=False, server_default="CREATED"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updatedAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_Project_userId_createdAt", "Project", ["userId", "createdAt"])
    op.create_table(
        "Upload",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("projectId", sa.String(), sa.ForeignKey("Project.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("imageUrl", sa.String(), nullable=False),
        sa.Column("fileName", sa.String(), nullable=False),
        sa.Column("mimeType", sa.String(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    for table_name, json_column in [
        ("Analysis", "analysisJson"),
        ("OcrResult", "ocrJson"),
        ("LayerData", "layersJson"),
        ("Storyboard", "storyboardJson"),
        ("MotionPlan", "motionPlanJson"),
    ]:
        columns = [
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("projectId", sa.String(), sa.ForeignKey("Project.id", ondelete="CASCADE"), nullable=False, unique=True),
            sa.Column(json_column, sa.JSON(), nullable=False),
            sa.Column("createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        ]
        if table_name == "OcrResult":
            columns.insert(3, sa.Column("warning", sa.Text(), nullable=True))
        op.create_table(table_name, *columns)

    op.create_table(
        "Evaluation",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("projectId", sa.String(), sa.ForeignKey("Project.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("evaluationJson", sa.JSON(), nullable=False),
        sa.Column("approved", sa.Boolean(), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_table(
        "Render",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("projectId", sa.String(), sa.ForeignKey("Project.id", ondelete="CASCADE"), nullable=False),
        sa.Column("videoUrl", sa.String(), nullable=True),
        sa.Column("format", sa.String(), nullable=False),
        sa.Column("renderStatus", render_status, nullable=False, server_default="QUEUED"),
        sa.Column("logs", sa.Text(), nullable=True),
        sa.Column("createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updatedAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_Render_projectId_renderStatus", "Render", ["projectId", "renderStatus"])
    op.create_table(
        "AgentLog",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("projectId", sa.String(), sa.ForeignKey("Project.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agentName", sa.String(), nullable=False),
        sa.Column("input", sa.JSON(), nullable=False),
        sa.Column("output", sa.JSON(), nullable=False),
        sa.Column("createdAt", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_AgentLog_projectId_createdAt", "AgentLog", ["projectId", "createdAt"])
    op.create_table(
        "PipelineStep",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("projectId", sa.String(), sa.ForeignKey("Project.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("status", pipeline_status, nullable=False, server_default="PENDING"),
        sa.Column("startedAt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("endedAt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("errorMessage", sa.Text(), nullable=True),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.UniqueConstraint("projectId", "key", name="uq_PipelineStep_projectId_key"),
    )
    op.create_index("ix_PipelineStep_projectId", "PipelineStep", ["projectId"])


def downgrade() -> None:
    for table in ["PipelineStep", "AgentLog", "Render", "Evaluation", "MotionPlan", "Storyboard", "LayerData", "OcrResult", "Analysis", "Upload", "Project", "User"]:
        op.drop_table(table)
    bind = op.get_bind()
    pipeline_status.drop(bind, checkfirst=True)
    render_status.drop(bind, checkfirst=True)
    project_status.drop(bind, checkfirst=True)

