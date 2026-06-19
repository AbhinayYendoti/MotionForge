from __future__ import annotations

import enum
import secrets
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def cuid() -> str:
    return "cm" + secrets.token_urlsafe(18).replace("-", "").replace("_", "")[:24]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ProjectStatus(str, enum.Enum):
    CREATED = "CREATED"
    UPLOADED = "UPLOADED"
    ANALYZING = "ANALYZING"
    EXTRACTING = "EXTRACTING"
    STORYBOARDING = "STORYBOARDING"
    PLANNING = "PLANNING"
    EVALUATING = "EVALUATING"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RenderStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PipelineStepStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class User(Base):
    __tablename__ = "User"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    clerk_id: Mapped[str] = mapped_column("clerkId", String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)

    projects: Mapped[list[Project]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "Project"
    __table_args__ = (Index("ix_Project_userId_createdAt", "userId", "createdAt"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    user_id: Mapped[str] = mapped_column("userId", ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    prompt: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus, name="ProjectStatus"), default=ProjectStatus.CREATED, nullable=False)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="projects")
    upload: Mapped[Upload | None] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")
    analysis: Mapped[Analysis | None] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")
    ocr_result: Mapped[OcrResult | None] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")
    layer_data: Mapped[LayerData | None] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")
    storyboard: Mapped[Storyboard | None] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")
    motion_plan: Mapped[MotionPlan | None] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")
    evaluation: Mapped[Evaluation | None] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")
    renders: Mapped[list[Render]] = relationship(back_populates="project", cascade="all, delete-orphan", order_by="desc(Render.created_at)")
    agent_logs: Mapped[list[AgentLog]] = relationship(back_populates="project", cascade="all, delete-orphan", order_by="desc(AgentLog.created_at)")
    pipeline: Mapped[list[PipelineStep]] = relationship(back_populates="project", cascade="all, delete-orphan", order_by="PipelineStep.id")


class Upload(Base):
    __tablename__ = "Upload"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    project_id: Mapped[str] = mapped_column("projectId", ForeignKey("Project.id", ondelete="CASCADE"), unique=True, nullable=False)
    image_url: Mapped[str] = mapped_column("imageUrl", String, nullable=False)
    file_name: Mapped[str] = mapped_column("fileName", String, nullable=False)
    mime_type: Mapped[str] = mapped_column("mimeType", String, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)

    project: Mapped[Project] = relationship(back_populates="upload")


class Analysis(Base):
    __tablename__ = "Analysis"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    project_id: Mapped[str] = mapped_column("projectId", ForeignKey("Project.id", ondelete="CASCADE"), unique=True, nullable=False)
    analysis_json: Mapped[dict] = mapped_column("analysisJson", JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
    project: Mapped[Project] = relationship(back_populates="analysis")


class OcrResult(Base):
    __tablename__ = "OcrResult"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    project_id: Mapped[str] = mapped_column("projectId", ForeignKey("Project.id", ondelete="CASCADE"), unique=True, nullable=False)
    ocr_json: Mapped[dict] = mapped_column("ocrJson", JSON, nullable=False)
    warning: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
    project: Mapped[Project] = relationship(back_populates="ocr_result")


class LayerData(Base):
    __tablename__ = "LayerData"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    project_id: Mapped[str] = mapped_column("projectId", ForeignKey("Project.id", ondelete="CASCADE"), unique=True, nullable=False)
    layers_json: Mapped[dict] = mapped_column("layersJson", JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
    project: Mapped[Project] = relationship(back_populates="layer_data")


class Storyboard(Base):
    __tablename__ = "Storyboard"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    project_id: Mapped[str] = mapped_column("projectId", ForeignKey("Project.id", ondelete="CASCADE"), unique=True, nullable=False)
    storyboard_json: Mapped[dict] = mapped_column("storyboardJson", JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
    project: Mapped[Project] = relationship(back_populates="storyboard")


class MotionPlan(Base):
    __tablename__ = "MotionPlan"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    project_id: Mapped[str] = mapped_column("projectId", ForeignKey("Project.id", ondelete="CASCADE"), unique=True, nullable=False)
    motion_plan_json: Mapped[dict] = mapped_column("motionPlanJson", JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
    project: Mapped[Project] = relationship(back_populates="motion_plan")


class Evaluation(Base):
    __tablename__ = "Evaluation"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    project_id: Mapped[str] = mapped_column("projectId", ForeignKey("Project.id", ondelete="CASCADE"), unique=True, nullable=False)
    evaluation_json: Mapped[dict] = mapped_column("evaluationJson", JSON, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
    project: Mapped[Project] = relationship(back_populates="evaluation")


class Render(Base):
    __tablename__ = "Render"
    __table_args__ = (Index("ix_Render_projectId_renderStatus", "projectId", "renderStatus"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    project_id: Mapped[str] = mapped_column("projectId", ForeignKey("Project.id", ondelete="CASCADE"), nullable=False)
    video_url: Mapped[str | None] = mapped_column("videoUrl", String)
    format: Mapped[str] = mapped_column(String, nullable=False)
    render_status: Mapped[RenderStatus] = mapped_column("renderStatus", Enum(RenderStatus, name="RenderStatus"), default=RenderStatus.QUEUED, nullable=False)
    logs: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    project: Mapped[Project] = relationship(back_populates="renders")


class AgentLog(Base):
    __tablename__ = "AgentLog"
    __table_args__ = (Index("ix_AgentLog_projectId_createdAt", "projectId", "createdAt"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    project_id: Mapped[str] = mapped_column("projectId", ForeignKey("Project.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column("agentName", String, nullable=False)
    input: Mapped[dict] = mapped_column(JSON, nullable=False)
    output: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), default=utcnow, nullable=False)

    project: Mapped[Project] = relationship(back_populates="agent_logs")


class PipelineStep(Base):
    __tablename__ = "PipelineStep"
    __table_args__ = (
        UniqueConstraint("projectId", "key", name="uq_PipelineStep_projectId_key"),
        Index("ix_PipelineStep_projectId", "projectId"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=cuid)
    project_id: Mapped[str] = mapped_column("projectId", ForeignKey("Project.id", ondelete="CASCADE"), nullable=False)
    key: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[PipelineStepStatus] = mapped_column(Enum(PipelineStepStatus, name="PipelineStepStatus"), default=PipelineStepStatus.PENDING, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column("startedAt", DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column("endedAt", DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column("errorMessage", Text)
    duration: Mapped[float | None] = mapped_column(Float)

    project: Mapped[Project] = relationship(back_populates="pipeline")

