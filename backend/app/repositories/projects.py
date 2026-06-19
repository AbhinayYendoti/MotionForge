from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import models

PIPELINE_STEPS = [
    ("upload", "Upload"),
    ("analysis", "Analysis"),
    ("ocr", "OCR"),
    ("layers", "Layer Extraction"),
    ("storyboard", "Storyboard"),
    ("motion", "Motion Planning"),
    ("evaluation", "Evaluation"),
    ("rendering", "Rendering"),
    ("completed", "Completed"),
]


def upsert_user(db: Session, clerk_id: str, email: str) -> models.User:
    user = db.scalar(select(models.User).where(models.User.clerk_id == clerk_id))
    if user:
        user.email = email
        return user
    user = models.User(clerk_id=clerk_id, email=email)
    db.add(user)
    db.flush()
    return user


def create_project(db: Session, user: models.User, title: str, prompt: str | None) -> models.Project:
    project = models.Project(user_id=user.id, title=title, prompt=prompt or None)
    db.add(project)
    db.flush()
    ensure_pipeline(db, project.id)
    return project


def ensure_pipeline(db: Session, project_id: str) -> None:
    existing = {step.key for step in db.scalars(select(models.PipelineStep).where(models.PipelineStep.project_id == project_id))}
    for key, label in PIPELINE_STEPS:
        if key not in existing:
            db.add(models.PipelineStep(project_id=project_id, key=key, label=label))
    db.flush()


def get_project(db: Session, user_id: str, project_id: str) -> models.Project | None:
    return db.scalar(
        select(models.Project)
        .where(models.Project.id == project_id, models.Project.user_id == user_id)
        .options(
            selectinload(models.Project.upload),
            selectinload(models.Project.analysis),
            selectinload(models.Project.ocr_result),
            selectinload(models.Project.layer_data),
            selectinload(models.Project.storyboard),
            selectinload(models.Project.motion_plan),
            selectinload(models.Project.evaluation),
            selectinload(models.Project.renders),
            selectinload(models.Project.pipeline),
            selectinload(models.Project.agent_logs),
        )
    )


def list_projects(db: Session, user_id: str) -> list[models.Project]:
    return list(
        db.scalars(
            select(models.Project)
            .where(models.Project.user_id == user_id)
            .order_by(models.Project.created_at.desc())
            .options(selectinload(models.Project.upload), selectinload(models.Project.renders), selectinload(models.Project.pipeline))
        )
    )


def dashboard_counts(db: Session, user_id: str) -> tuple[int, int]:
    render_count = db.scalar(select(func.count(models.Render.id)).join(models.Project).where(models.Project.user_id == user_id)) or 0
    completed_count = db.scalar(
        select(func.count(models.Project.id)).where(models.Project.user_id == user_id, models.Project.status == models.ProjectStatus.COMPLETED)
    ) or 0
    return int(render_count), int(completed_count)


def set_project_status(db: Session, project: models.Project, status: models.ProjectStatus, error: str | None = None) -> None:
    project.status = status
    project.error = error
    project.updated_at = models.utcnow()
    db.flush()


def set_step(db: Session, project_id: str, key: str, status: models.PipelineStepStatus, error_message: str | None = None) -> None:
    step = db.scalar(select(models.PipelineStep).where(models.PipelineStep.project_id == project_id, models.PipelineStep.key == key))
    if not step:
        ensure_pipeline(db, project_id)
        step = db.scalar(select(models.PipelineStep).where(models.PipelineStep.project_id == project_id, models.PipelineStep.key == key))
    if not step:
        raise RuntimeError(f"Pipeline step {key} could not be created.")
    now = models.utcnow()
    step.status = status
    if status == models.PipelineStepStatus.RUNNING:
        step.started_at = now
        step.ended_at = None
        step.duration = None
        step.error_message = None
    if status in {models.PipelineStepStatus.COMPLETED, models.PipelineStepStatus.FAILED}:
        step.ended_at = now
        step.error_message = error_message
        if step.started_at:
            started_at = step.started_at if step.started_at.tzinfo else step.started_at.replace(tzinfo=timezone.utc)
            ended_at = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
            step.duration = max(0, (ended_at - started_at).total_seconds())
    db.flush()


def log_agent(db: Session, project_id: str, agent_name: str, input_data: dict[str, Any], output_data: dict[str, Any]) -> None:
    db.add(models.AgentLog(project_id=project_id, agent_name=agent_name, input=input_data, output=output_data))
    db.flush()


def upsert_singleton(db: Session, cls: type, project_id: str, **values: Any) -> Any:
    record = db.scalar(select(cls).where(cls.project_id == project_id))
    if record:
        for key, value in values.items():
            setattr(record, key, value)
    else:
        record = cls(project_id=project_id, **values)
        db.add(record)
    db.flush()
    return record


def serialize_project(project: models.Project) -> dict[str, Any]:
    def dt(value: datetime | None) -> datetime | None:
        return value

    def upload() -> dict[str, Any] | None:
        item = project.upload
        if not item:
            return None
        return {
            "id": item.id,
            "imageUrl": item.image_url,
            "fileName": item.file_name,
            "mimeType": item.mime_type,
            "width": item.width,
            "height": item.height,
            "size": item.size,
            "createdAt": dt(item.created_at),
        }

    def json_record(item: Any, key: str) -> dict[str, Any] | None:
        if not item:
            return None
        payload = {"id": item.id, "createdAt": dt(item.created_at), key: getattr(item, _snake(key))}
        if hasattr(item, "approved"):
            payload["approved"] = item.approved
        if hasattr(item, "warning"):
            payload["warning"] = item.warning
        return payload

    return {
        "id": project.id,
        "title": project.title,
        "prompt": project.prompt,
        "status": project.status.value,
        "error": project.error,
        "createdAt": dt(project.created_at),
        "updatedAt": dt(project.updated_at),
        "upload": upload(),
        "analysis": json_record(project.analysis, "analysisJson"),
        "ocrResult": json_record(project.ocr_result, "ocrJson"),
        "layerData": json_record(project.layer_data, "layersJson"),
        "storyboard": json_record(project.storyboard, "storyboardJson"),
        "motionPlan": json_record(project.motion_plan, "motionPlanJson"),
        "evaluation": json_record(project.evaluation, "evaluationJson"),
        "renders": [
            {
                "id": item.id,
                "videoUrl": item.video_url,
                "format": item.format,
                "renderStatus": item.render_status.value,
                "logs": item.logs,
                "createdAt": dt(item.created_at),
                "updatedAt": dt(item.updated_at),
            }
            for item in project.renders
        ],
        "pipeline": [
            {
                "id": item.id,
                "key": item.key,
                "label": item.label,
                "status": item.status.value,
                "startedAt": dt(item.started_at),
                "endedAt": dt(item.ended_at),
                "errorMessage": item.error_message,
                "duration": item.duration,
            }
            for item in sorted(project.pipeline, key=lambda step: [k for k, _ in PIPELINE_STEPS].index(step.key) if step.key in dict(PIPELINE_STEPS) else 999)
        ],
        "agentLogs": [
            {
                "id": item.id,
                "agentName": item.agent_name,
                "input": item.input,
                "output": item.output,
                "createdAt": dt(item.created_at),
            }
            for item in project.agent_logs
        ],
    }


def _snake(camel: str) -> str:
    mapping = {
        "analysisJson": "analysis_json",
        "ocrJson": "ocr_json",
        "layersJson": "layers_json",
        "storyboardJson": "storyboard_json",
        "motionPlanJson": "motion_plan_json",
        "evaluationJson": "evaluation_json",
    }
    return mapping[camel]
