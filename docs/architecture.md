# MotionForge Architecture

MotionForge now uses a split production architecture: Next.js for the customer-facing application and FastAPI for backend orchestration.

## Runtime Diagram

Next.js App Router frontend
-> Clerk session token
-> FastAPI authenticated endpoints
-> SQLAlchemy repositories
-> Neon PostgreSQL
-> NVIDIA agents
-> Pipeline orchestration
-> Background render job
-> Remotion renderer
-> MP4 in public/renders or production storage

## Backend Folder Structure

- backend/app/api: FastAPI route modules and dependencies.
- backend/app/agents: visual understanding, OCR, layer extraction, storyboard, motion director, and evaluation agents.
- backend/app/core: configuration, logging, and Clerk token verification.
- backend/app/database: SQLAlchemy engine, sessions, models, and enums.
- backend/app/repositories: database access and serialization boundaries.
- backend/app/schemas: Pydantic v2 request and response contracts.
- backend/app/services: storage, NVIDIA client, image helpers, and pipeline orchestration.
- backend/app/workers: background render worker.
- backend/alembic: migration environment and versions.

## FastAPI Endpoints

- GET /health
- GET /projects
- GET /project/{project_id}
- POST /project/create
- POST /analyze
- POST /ocr
- POST /extract-layers
- POST /storyboard
- POST /motion-plan
- POST /evaluate
- POST /render
- POST /pipeline/run

## SQLAlchemy Models

- User
- Project
- Upload
- Analysis
- OcrResult
- LayerData
- Storyboard
- MotionPlan
- Evaluation
- Render
- AgentLog
- PipelineStep

## Pipeline Contract

Upload -> Analysis -> OCR -> Layer Extraction -> Storyboard -> Motion Planning -> Evaluation -> Rendering -> Completed.

Every PipelineStep stores status, startedAt, endedAt, errorMessage, and duration. Render work is queued with FastAPI BackgroundTasks so API requests do not block on MP4 generation.

## Removed Node Backend Dependencies

- Prisma
- @prisma/client
- tesseract.js
- sharp as an app-level image-processing dependency
- next-safe-action

