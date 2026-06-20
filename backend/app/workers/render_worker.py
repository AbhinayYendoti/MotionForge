import json
import subprocess
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import REPO_ROOT, settings
from app.core.logging import logger
from app.database import models
from app.database.session import SessionLocal
from app.repositories import projects as project_repo


def run_render_job(render_id: str) -> None:
    db: Session = SessionLocal()
    # Initialise path sentinels so the finally block can always clean up safely.
    job_path: Path | None = None
    output_path: Path | None = None

    try:
        render = db.get(models.Render, render_id)
        if not render:
            logger.error("Render job missing render row", extra={"render_id": render_id})
            return
        project = project_repo.get_project(db, render.project.user_id, render.project_id)
        if not project or not project.upload or not project.storyboard or not project.motion_plan or not project.layer_data:
            raise RuntimeError("Render job is missing required project data (upload/storyboard/motion_plan/layer_data).")

        render.render_status = models.RenderStatus.RENDERING
        db.commit()

        # ── Build the per-render job manifest ─────────────────────────────────
        job_dir = REPO_ROOT / "backend" / ".render-jobs"
        job_dir.mkdir(parents=True, exist_ok=True)
        job_path = job_dir / f"{render.id}.json"

        output_name = f"{project.id}-{render.format}-{render.id}.mp4"
        output_path = REPO_ROOT / settings.render_dir / output_name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        job_path.write_text(
            json.dumps(
                {
                    "outputLocation": str(output_path),
                    "format": render.format,
                    "imageUrl": project.upload.image_url,
                    "storyboard": project.storyboard.storyboard_json,
                    "motionPlan": project.motion_plan.motion_plan_json,
                    "layers": project.layer_data.layers_json,
                    "analysis": project.analysis.analysis_json if project.analysis else None,
                }
            ),
            encoding="utf-8",
        )

        logger.info(
            "Starting Remotion render subprocess",
            extra={"render_id": render_id, "format": render.format},
        )

        # ── Invoke Remotion via Node subprocess ───────────────────────────────
        process = subprocess.run(
            [settings.node_binary, "backend/remotion_render.mjs", str(job_path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        if process.returncode != 0:
            raise RuntimeError(
                (process.stderr or process.stdout or "Remotion render exited with non-zero code").strip()
            )

        # ── Store the video — UploadThing in production, local path in dev ────
        video_url: str
        if settings.uploadthing_secret:
            # Production: upload MP4 to UploadThing CDN.
            # Read bytes into memory BEFORE we enter the finally cleanup block,
            # so that the finally block cannot delete the file while S3 is still
            # receiving data if we ever switch to a streaming upload.
            from app.services.uploadthing_service import upload_file_to_ut  # lazy import

            logger.info("Uploading rendered MP4 to UploadThing", extra={"render_id": render_id})
            video_url = upload_file_to_ut(settings.uploadthing_secret, output_path, output_name)
            # Upload is fully confirmed — safe to delete the local temp file now.
            # We set output_path to None so the finally block doesn't double-delete.
            _cleanup_file(output_path)
            output_path = None
        else:
            # Development fallback: serve via Next.js /public/renders/ static route.
            video_url = f"/renders/{output_name}"
            # Don't delete the local file in dev — it IS the asset.
            output_path = None  # Prevent finally from deleting it.
            logger.info(
                "UPLOADTHING_SECRET not set — MP4 stored locally (dev mode only)",
                extra={"video_url": video_url},
            )

        render.video_url = video_url
        render.logs = (process.stdout or f"Rendered {render.format} video.").strip()
        render.render_status = models.RenderStatus.COMPLETED
        project_repo.set_step(db, project.id, "rendering", models.PipelineStepStatus.COMPLETED)
        project_repo.set_step(db, project.id, "completed", models.PipelineStepStatus.COMPLETED)
        project_repo.set_project_status(db, project, models.ProjectStatus.COMPLETED)
        db.commit()

        logger.info(
            "Render job completed",
            extra={"render_id": render_id, "video_url": video_url},
        )

    except Exception as error:
        db.rollback()
        render = db.get(models.Render, render_id)
        if render:
            render.render_status = models.RenderStatus.FAILED
            render.logs = str(error)
            project = render.project
            project_repo.set_step(
                db, render.project_id, "rendering", models.PipelineStepStatus.FAILED, str(error)
            )
            project_repo.set_project_status(db, project, models.ProjectStatus.FAILED, str(error))
            db.commit()
        logger.exception("Render job failed", extra={"render_id": render_id, "error": str(error)})

    finally:
        db.close()
        # Always remove the job manifest and any leftover temp output.
        _cleanup_file(job_path)
        _cleanup_file(output_path)


def _cleanup_file(path: Path | None) -> None:
    """Silently delete a file if it exists. Never raises."""
    try:
        if path and path.exists():
            path.unlink()
    except Exception as exc:
        logger.warning("Failed to clean up temp file", extra={"path": str(path), "error": str(exc)})
