import asyncio

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.agents.evaluation_agent import run_evaluation_agent
from app.agents.layer_extraction import run_layer_extraction_engine
from app.agents.motion_director import run_motion_director_agent
from app.agents.ocr_agent import run_ocr_agent
from app.agents.storyboard_agent import run_storyboard_agent
from app.agents.visual_understanding import run_visual_understanding_agent
from app.database import models
from app.database.session import SessionLocal
from app.repositories import projects as project_repo
from app.schemas.pipeline import Evaluation, LayerExtraction, MotionPlan, OcrResult, Storyboard, VisualAnalysis
from app.workers.render_worker import run_render_job

# Maximum number of regeneration attempts when evaluation rejects the plan
_MAX_PIPELINE_RETRIES = 2


async def analyze_project(db: Session, project: models.Project) -> VisualAnalysis:
    if not project.upload:
        raise ValueError("Project upload is required before analysis.")
    project_repo.set_project_status(db, project, models.ProjectStatus.ANALYZING)
    project_repo.set_step(db, project.id, "analysis", models.PipelineStepStatus.RUNNING)
    try:
        output = await run_visual_understanding_agent(project.upload.image_url, project.prompt)
        project_repo.upsert_singleton(db, models.Analysis, project.id, analysis_json=output.model_dump())
        project_repo.log_agent(db, project.id, "Visual Understanding Agent", {"imageUrl": project.upload.image_url, "prompt": project.prompt}, output.model_dump())
        project_repo.set_step(db, project.id, "analysis", models.PipelineStepStatus.COMPLETED)
        db.commit()
        return output
    except Exception as error:
        project_repo.set_step(db, project.id, "analysis", models.PipelineStepStatus.FAILED, str(error))
        project_repo.set_project_status(db, project, models.ProjectStatus.FAILED, str(error))
        db.commit()
        raise


async def ocr_project(db: Session, project: models.Project) -> OcrResult:
    if not project.upload:
        raise ValueError("Project upload is required before OCR.")
    project_repo.set_step(db, project.id, "ocr", models.PipelineStepStatus.RUNNING)
    output = await run_ocr_agent(project.upload.image_url)
    project_repo.upsert_singleton(db, models.OcrResult, project.id, ocr_json=output.model_dump(), warning=output.warning)
    project_repo.log_agent(db, project.id, "OCR Agent", {"imageUrl": project.upload.image_url}, output.model_dump())
    project_repo.set_step(db, project.id, "ocr", models.PipelineStepStatus.COMPLETED)
    db.commit()
    return output


async def extract_layers_project(db: Session, project: models.Project, ocr: OcrResult | None = None) -> LayerExtraction:
    if not project.upload:
        raise ValueError("Project upload is required before layer extraction.")
    active_ocr = ocr or (OcrResult.model_validate(project.ocr_result.ocr_json) if project.ocr_result else await ocr_project(db, project))
    project_repo.set_project_status(db, project, models.ProjectStatus.EXTRACTING)
    project_repo.set_step(db, project.id, "layers", models.PipelineStepStatus.RUNNING)
    try:
        output = await run_layer_extraction_engine(project.upload.image_url, active_ocr)
    except Exception:
        output = await run_layer_extraction_engine(project.upload.image_url, None)
    project_repo.upsert_singleton(db, models.LayerData, project.id, layers_json=output.model_dump())
    project_repo.log_agent(db, project.id, "Layer Extraction Engine", {"imageUrl": project.upload.image_url, "ocr": active_ocr.model_dump()}, output.model_dump())
    project_repo.set_step(db, project.id, "layers", models.PipelineStepStatus.COMPLETED)
    db.commit()
    return output


async def storyboard_project(
    db: Session,
    project: models.Project,
    layers: LayerExtraction | None = None,
    negative_guidance: list[str] | None = None,
) -> Storyboard:
    if not project.analysis:
        await analyze_project(db, project)
        project = project_repo.get_project(db, project.user_id, project.id) or project
    active_layers = layers or (LayerExtraction.model_validate(project.layer_data.layers_json) if project.layer_data else await extract_layers_project(db, project))
    analysis = VisualAnalysis.model_validate(project.analysis.analysis_json)
    project_repo.set_project_status(db, project, models.ProjectStatus.STORYBOARDING)
    project_repo.set_step(db, project.id, "storyboard", models.PipelineStepStatus.RUNNING)
    output = await run_storyboard_agent(project.prompt, analysis, active_layers, negative_guidance=negative_guidance)
    project_repo.upsert_singleton(db, models.Storyboard, project.id, storyboard_json=output.model_dump())
    project_repo.log_agent(db, project.id, "Storyboard Agent", {"analysis": analysis.model_dump(), "layers": active_layers.model_dump()}, output.model_dump())
    project_repo.set_step(db, project.id, "storyboard", models.PipelineStepStatus.COMPLETED)
    db.commit()
    return output


async def motion_plan_project(db: Session, project: models.Project, storyboard: Storyboard | None = None, layers: LayerExtraction | None = None) -> MotionPlan:
    active_storyboard = storyboard or (Storyboard.model_validate(project.storyboard.storyboard_json) if project.storyboard else await storyboard_project(db, project))
    active_layers = layers or (LayerExtraction.model_validate(project.layer_data.layers_json) if project.layer_data else await extract_layers_project(db, project))
    project_repo.set_project_status(db, project, models.ProjectStatus.PLANNING)
    project_repo.set_step(db, project.id, "motion", models.PipelineStepStatus.RUNNING)
    output = await run_motion_director_agent(active_storyboard, active_layers)
    project_repo.upsert_singleton(db, models.MotionPlan, project.id, motion_plan_json=output.model_dump())
    project_repo.log_agent(db, project.id, "Motion Director Agent", {"storyboard": active_storyboard.model_dump(), "layers": active_layers.model_dump()}, output.model_dump())
    project_repo.set_step(db, project.id, "motion", models.PipelineStepStatus.COMPLETED)
    db.commit()
    return output


async def evaluate_project(
    db: Session,
    project: models.Project,
    layers: LayerExtraction | None = None,
    storyboard: Storyboard | None = None,
    motion_plan: MotionPlan | None = None,
) -> Evaluation:
    if not project.analysis:
        await analyze_project(db, project)
        project = project_repo.get_project(db, project.user_id, project.id) or project
    active_layers = layers or (LayerExtraction.model_validate(project.layer_data.layers_json) if project.layer_data else await extract_layers_project(db, project))
    active_storyboard = storyboard or (Storyboard.model_validate(project.storyboard.storyboard_json) if project.storyboard else await storyboard_project(db, project, active_layers))
    active_motion_plan = motion_plan or (
        MotionPlan.model_validate(project.motion_plan.motion_plan_json) if project.motion_plan else await motion_plan_project(db, project, active_storyboard, active_layers)
    )
    analysis = VisualAnalysis.model_validate(project.analysis.analysis_json)
    project_repo.set_project_status(db, project, models.ProjectStatus.EVALUATING)
    project_repo.set_step(db, project.id, "evaluation", models.PipelineStepStatus.RUNNING)
    output = await run_evaluation_agent(analysis, active_layers, active_storyboard, active_motion_plan)
    project_repo.upsert_singleton(db, models.Evaluation, project.id, evaluation_json=output.model_dump(), approved=output.approved)
    project_repo.log_agent(db, project.id, "Evaluation Agent", {"storyboard": active_storyboard.model_dump(), "motionPlan": active_motion_plan.model_dump()}, output.model_dump())
    project_repo.set_step(db, project.id, "evaluation", models.PipelineStepStatus.COMPLETED if output.approved else models.PipelineStepStatus.FAILED)
    if not output.approved:
        project_repo.set_project_status(db, project, models.ProjectStatus.FAILED, "; ".join(output.regenerationReasons) or "Evaluation rejected this motion plan.")
    db.commit()
    return output


async def run_pipeline(db: Session, project: models.Project, render_format: str, background_tasks: BackgroundTasks | None = None) -> models.Render | None:
    if not project.upload:
        raise ValueError("Project upload is required before rendering.")

    # ── Phase 1: Analysis, OCR, Layer extraction (run once) ───────────────
    analysis = VisualAnalysis.model_validate(project.analysis.analysis_json) if project.analysis else await analyze_project(db, project)
    project = project_repo.get_project(db, project.user_id, project.id) or project
    ocr = OcrResult.model_validate(project.ocr_result.ocr_json) if project.ocr_result else await ocr_project(db, project)
    project = project_repo.get_project(db, project.user_id, project.id) or project
    layers = LayerExtraction.model_validate(project.layer_data.layers_json) if project.layer_data else await extract_layers_project(db, project, ocr)
    project = project_repo.get_project(db, project.user_id, project.id) or project

    # ── Phase 2: Storyboard → Motion → Evaluation (with retry loop) ───────
    negative_guidance: list[str] | None = None
    evaluation: Evaluation | None = None

    for attempt in range(_MAX_PIPELINE_RETRIES + 1):
        if attempt > 0:
            logger.info(
                "Regenerating storyboard after evaluation rejection",
                extra={"project_id": project.id, "attempt": attempt, "reasons": negative_guidance},
            )
        storyboard = await storyboard_project(db, project, layers, negative_guidance=negative_guidance)
        project = project_repo.get_project(db, project.user_id, project.id) or project
        motion_plan = await motion_plan_project(db, project, storyboard, layers)
        project = project_repo.get_project(db, project.user_id, project.id) or project
        evaluation = await evaluate_project(db, project, layers, storyboard, motion_plan)

        if evaluation.approved:
            break

        # Capture rejection reasons for the next attempt
        if attempt < _MAX_PIPELINE_RETRIES and evaluation.regenerationReasons:
            negative_guidance = evaluation.regenerationReasons
            # Reset project status so the next iteration can proceed
            project_repo.set_project_status(db, project, models.ProjectStatus.STORYBOARDING)
            db.commit()
            project = project_repo.get_project(db, project.user_id, project.id) or project
        else:
            # Exhausted retries or no guidance available
            return None

    if not evaluation or not evaluation.approved:
        return None

    # ── Phase 3: Render ───────────────────────────────────────────────────
    project_repo.set_project_status(db, project, models.ProjectStatus.RENDERING)
    project_repo.set_step(db, project.id, "rendering", models.PipelineStepStatus.RUNNING)
    render = models.Render(project_id=project.id, format=render_format, render_status=models.RenderStatus.QUEUED)
    db.add(render)
    db.commit()
    db.refresh(render)
    if background_tasks:
        background_tasks.add_task(run_render_job, render.id)
    else:
        await asyncio.to_thread(run_render_job, render.id)
    return render


async def run_pipeline_job(project_id: str, user_id: str, render_format: str) -> None:
    db = SessionLocal()
    try:
        project = project_repo.get_project(db, user_id, project_id)
        if not project:
            logger.error("Pipeline job missing project", extra={"project_id": project_id, "user_id": user_id})
            return
        await run_pipeline(db, project, render_format)
    except Exception as error:
        db.rollback()
        project = project_repo.get_project(db, user_id, project_id)
        if project:
            project_repo.set_project_status(db, project, models.ProjectStatus.FAILED, str(error))
            db.commit()
        logger.exception("Pipeline job failed", extra={"project_id": project_id})
    finally:
        db.close()
