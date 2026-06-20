from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_db_user
from app.database import models
from app.database.session import get_db
from app.repositories import projects as project_repo
from app.schemas.project import DashboardOut, PipelineRunIn, PipelineRunOut, ProjectOut
from app.services.pipeline_service import (
    analyze_project,
    evaluate_project,
    extract_layers_project,
    motion_plan_project,
    ocr_project,
    run_pipeline_job,
    storyboard_project,
)
from app.services.storage_service import store_upload

router = APIRouter(tags=["projects"])

ACTIVE_PIPELINE_STATUSES = {
    models.ProjectStatus.ANALYZING,
    models.ProjectStatus.EXTRACTING,
    models.ProjectStatus.STORYBOARDING,
    models.ProjectStatus.PLANNING,
    models.ProjectStatus.EVALUATING,
    models.ProjectStatus.RENDERING,
}


def _project_or_404(db: Session, user: models.User, project_id: str) -> models.Project:
    project = project_repo.get_project(db, user.id, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.get("/projects", response_model=DashboardOut)
def list_dashboard(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_db_user)],
):
    projects = project_repo.list_projects(db, user.id)
    render_count, completed_count = project_repo.dashboard_counts(db, user.id)
    return {"projects": [project_repo.serialize_project(project) for project in projects], "renderCount": render_count, "completedCount": completed_count}


@router.get("/project/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_db_user)],
):
    project = _project_or_404(db, user, project_id)
    return project_repo.serialize_project(project)


@router.post("/project/create", response_model=ProjectOut)
async def create_project(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_db_user)],
    title: Annotated[str, Form(min_length=2, max_length=120)],
    prompt: Annotated[str | None, Form()] = None,
    imageUrl: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile | None, File()] = None,
):
    project = project_repo.create_project(db, user, title, prompt)
    if file and file.filename:
        upload = await store_upload(file)
        db.add(models.Upload(project_id=project.id, **upload))
    elif imageUrl:
        db.add(models.Upload(project_id=project.id, image_url=imageUrl, file_name="remote-image", mime_type="image/remote", size=0))
    else:
        raise HTTPException(status_code=400, detail="Upload an image or provide a remote image URL.")
    project_repo.set_step(db, project.id, "upload", models.PipelineStepStatus.COMPLETED)
    project_repo.set_project_status(db, project, models.ProjectStatus.UPLOADED)
    db.commit()
    project = _project_or_404(db, user, project.id)
    return project_repo.serialize_project(project)


@router.post("/analyze")
async def analyze(payload: PipelineRunIn, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(get_current_db_user)]):
    project = _project_or_404(db, user, payload.projectId)
    return (await analyze_project(db, project)).model_dump()


@router.post("/ocr")
async def ocr(payload: PipelineRunIn, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(get_current_db_user)]):
    project = _project_or_404(db, user, payload.projectId)
    return (await ocr_project(db, project)).model_dump()


@router.post("/extract-layers")
async def extract_layers(payload: PipelineRunIn, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(get_current_db_user)]):
    project = _project_or_404(db, user, payload.projectId)
    return (await extract_layers_project(db, project)).model_dump()


@router.post("/storyboard")
async def storyboard(payload: PipelineRunIn, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(get_current_db_user)]):
    project = _project_or_404(db, user, payload.projectId)
    return (await storyboard_project(db, project)).model_dump()


@router.post("/motion-plan")
async def motion_plan(payload: PipelineRunIn, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(get_current_db_user)]):
    project = _project_or_404(db, user, payload.projectId)
    return (await motion_plan_project(db, project)).model_dump()


@router.post("/evaluate")
async def evaluate(payload: PipelineRunIn, db: Annotated[Session, Depends(get_db)], user: Annotated[models.User, Depends(get_current_db_user)]):
    project = _project_or_404(db, user, payload.projectId)
    return (await evaluate_project(db, project)).model_dump()


@router.post("/render", response_model=PipelineRunOut)
@router.post("/pipeline/run", response_model=PipelineRunOut)
async def run_pipeline_endpoint(
    payload: PipelineRunIn,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_db_user)],
):
    project = _project_or_404(db, user, payload.projectId)
    if project.status not in ACTIVE_PIPELINE_STATUSES:
        project_repo.set_project_status(db, project, models.ProjectStatus.ANALYZING)
        project_repo.set_step(db, project.id, "analysis", models.PipelineStepStatus.RUNNING)
        db.commit()
        background_tasks.add_task(run_pipeline_job, project.id, user.id, payload.format)
    project = _project_or_404(db, user, payload.projectId)
    return {"project": project_repo.serialize_project(project), "renderId": None, "queued": True}


@router.delete("/project/{project_id}")
def delete_project(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_db_user)],
):
    project = _project_or_404(db, user, project_id)
    db.delete(project)
    db.commit()
    return {"success": True}
