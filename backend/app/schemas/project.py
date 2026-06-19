from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class UploadOut(BaseModel):
    id: str
    imageUrl: str
    fileName: str
    mimeType: str
    width: int | None
    height: int | None
    size: int
    createdAt: datetime


class JsonRecordOut(BaseModel):
    id: str
    createdAt: datetime
    analysisJson: dict[str, Any] | None = None
    ocrJson: dict[str, Any] | None = None
    layersJson: dict[str, Any] | None = None
    storyboardJson: dict[str, Any] | None = None
    motionPlanJson: dict[str, Any] | None = None
    evaluationJson: dict[str, Any] | None = None
    approved: bool | None = None
    warning: str | None = None


class RenderOut(BaseModel):
    id: str
    videoUrl: str | None
    format: str
    renderStatus: str
    logs: str | None
    createdAt: datetime
    updatedAt: datetime


class AgentLogOut(BaseModel):
    id: str
    agentName: str
    input: dict[str, Any]
    output: dict[str, Any]
    createdAt: datetime


class PipelineStepOut(BaseModel):
    id: str
    key: str
    label: str
    status: str
    startedAt: datetime | None
    endedAt: datetime | None
    errorMessage: str | None
    duration: float | None


class ProjectOut(BaseModel):
    id: str
    title: str
    prompt: str | None
    status: str
    error: str | None
    createdAt: datetime
    updatedAt: datetime
    upload: UploadOut | None
    analysis: JsonRecordOut | None
    ocrResult: JsonRecordOut | None
    layerData: JsonRecordOut | None
    storyboard: JsonRecordOut | None
    motionPlan: JsonRecordOut | None
    evaluation: JsonRecordOut | None
    renders: list[RenderOut]
    pipeline: list[PipelineStepOut]
    agentLogs: list[AgentLogOut]


class DashboardOut(BaseModel):
    projects: list[ProjectOut]
    renderCount: int
    completedCount: int


class PipelineRunIn(BaseModel):
    projectId: str
    format: Literal["reel", "landscape", "square"] = "reel"


class PipelineRunOut(BaseModel):
    project: ProjectOut
    renderId: str | None = None
    queued: bool = False

