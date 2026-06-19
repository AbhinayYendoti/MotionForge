# MotionForge AI

> Turn static marketing creatives into motion campaigns — driven by NVIDIA Build, rendered by Remotion.

MotionForge is a full-stack AI pipeline that takes a static image (product photo, ad creative, poster) and produces a professional MP4 motion-graphics video through a structured, explainable generation pipeline.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Pipeline Stages](#pipeline-stages)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
  - [Database — Neon PostgreSQL](#database--neon-postgresql)
  - [Backend — Render](#backend--render)
  - [Frontend — Vercel](#frontend--vercel)
- [Database Migrations](#database-migrations)
- [Production Checklist](#production-checklist)

---

## Overview

MotionForge transforms a static creative in ~60–90 seconds:

1. User uploads an image → stored on **UploadThing CDN**
2. **NVIDIA vision model** analyses the creative (brand, colours, hierarchy, style)
3. **OCR agent** extracts visible text and bounding boxes
4. **Layer extraction engine** decomposes the creative into animatable layers
5. **Storyboard agent** writes a scene-by-scene motion script
6. **Motion director** converts scenes into frame-level animation JSON
7. **Evaluation agent** scores the plan and retries if quality gates fail
8. **Remotion** renders the JSON into an MP4 uploaded to UploadThing
9. User downloads the finished video via a CDN URL

Every stage is visible in the dashboard pipeline rail.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 (App Router) + TypeScript |
| Styling | Tailwind CSS + Framer Motion |
| Auth | Clerk |
| File storage | UploadThing |
| Backend | FastAPI + Python 3.12 |
| Database | Neon PostgreSQL (SQLAlchemy 2 / Alembic) |
| AI | NVIDIA Build API (Llama-3.1, Llama-3.2-Vision, Nemotron) |
| Rendering | Remotion 4 + Node.js 22 |
| Frontend hosting | Vercel |
| Backend hosting | Render |

---

## Architecture

```
Browser
  │  Clerk auth (JWT)
  │  UploadThing upload (image → CDN)
  ▼
Next.js (Vercel)
  │  Server Actions / API routes
  │  Bearer token forwarded
  ▼
FastAPI (Render)
  │  Clerk JWT verification
  │  AI pipeline (async)
  │  Background render task
  ▼
Neon PostgreSQL      UploadThing CDN
(project state)      (images + MP4s)
```

---

## Pipeline Stages

| Stage | Agent | Fallback |
|-------|-------|---------|
| Visual Analysis | NVIDIA Vision | Simplified fallback object |
| OCR | pytesseract → NVIDIA Vision OCR | Empty OCR (pipeline continues) |
| Layer Extraction | NVIDIA Text | Minimal fallback layer set |
| Storyboard | NVIDIA Text | — |
| Motion Planning | NVIDIA Text | — |
| Evaluation | NVIDIA Nemotron | Soft pass (approved=true) |
| Render | Remotion + Node 22 | Marked FAILED, state preserved |

---

## Local Development

### Prerequisites

- Node.js ≥ 22
- Python 3.12
- A running PostgreSQL instance (or Neon free tier)
- Accounts: Clerk, UploadThing, NVIDIA Build

### Setup

```bash
# 1. Clone
git clone https://github.com/your-org/motionforge-ai.git
cd motionforge-ai

# 2. Install frontend dependencies
npm install

# 3. Copy and fill in environment variables
cp .env.example .env
# Edit .env with your real keys

# 4. Install backend dependencies
cd backend
pip install -r requirements.txt

# 5. Run database migrations
python -m alembic upgrade head
cd ..

# 6. Start both servers (two terminals)
# Terminal 1 — frontend
npm run dev

# Terminal 2 — backend
npm run backend:dev
```

Frontend: http://localhost:3000  
Backend: http://localhost:8000  
API docs: http://localhost:8000/docs

---

## Environment Variables

Copy `.env.example` to `.env` and fill in all values.

### Required for all environments

| Variable | Where to get it |
|----------|----------------|
| `DATABASE_URL` | Neon dashboard → Connection string |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk dashboard → API Keys |
| `CLERK_SECRET_KEY` | Clerk dashboard → API Keys |
| `NVIDIA_API_KEY` | https://build.nvidia.com → API Keys |
| `UPLOADTHING_TOKEN` | UploadThing dashboard → API Keys |
| `UPLOADTHING_SECRET` | UploadThing dashboard → API Keys |
| `UPLOADTHING_APP_ID` | UploadThing dashboard → App ID |

### Required in production

| Variable | Value |
|----------|-------|
| `BACKEND_URL` | Your Render service URL (server-side only) |
| `NEXT_PUBLIC_BACKEND_URL` | Your Render service URL (client-side) |
| `BACKEND_CORS_ORIGINS` | Your Vercel frontend URL |
| `APP_URL` | Your Vercel frontend URL |

---

## Deployment

### Database — Neon PostgreSQL

1. Create a project at https://console.neon.tech
2. Copy the **Connection string** (includes `?sslmode=require`)
3. Set it as `DATABASE_URL` in both Render and (for migrations) locally

Run migrations after every deploy:
```bash
cd backend
DATABASE_URL="<your-neon-url>" python -m alembic upgrade head
```

> Render automatically runs migrations as part of its build command (`alembic upgrade head`).

---

### Backend — Render

1. Connect your GitHub repo to [Render](https://render.com)
2. Create a **new Web Service**
3. Render detects `render.yaml` automatically — accept the detected settings
4. In **Environment → Environment Variables**, add all `sync: false` variables from `render.yaml`:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Neon connection string |
| `CLERK_SECRET_KEY` | Clerk secret |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk publishable key |
| `NVIDIA_API_KEY` | NVIDIA API key |
| `UPLOADTHING_TOKEN` | UploadThing token |
| `UPLOADTHING_SECRET` | UploadThing secret (`sk_live_...`) |
| `UPLOADTHING_APP_ID` | UploadThing app ID |
| `BACKEND_CORS_ORIGINS` | `https://your-project.vercel.app` |
| `APP_URL` | `https://your-project.vercel.app` |

5. Deploy — Render runs `pip install && npm ci && alembic upgrade head` then starts uvicorn
6. Verify: `https://your-api.onrender.com/health` → `{"status":"ok"}`

> **Note**: First deploy on a cold Render starter instance may take 60–90 s to wake up.

---

### Frontend — Vercel

1. Import your GitHub repo at https://vercel.com/new
2. Framework: **Next.js** (auto-detected)
3. Add **Environment Variables** in the Vercel dashboard:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk publishable key |
| `CLERK_SECRET_KEY` | Clerk secret key |
| `NEXT_PUBLIC_BACKEND_URL` | `https://your-api.onrender.com` |
| `BACKEND_URL` | `https://your-api.onrender.com` |
| `UPLOADTHING_TOKEN` | UploadThing token |
| `UPLOADTHING_SECRET` | UploadThing secret |
| `UPLOADTHING_APP_ID` | UploadThing app ID |
| `APP_URL` | `https://your-project.vercel.app` |

4. Deploy — Vercel runs `npm ci && npm run build`
5. Set **Allowed redirect URLs** in Clerk dashboard: `https://your-project.vercel.app`
6. Set **Allowed origins** in Clerk dashboard for your production domain

---

## Database Migrations

```bash
# Apply all pending migrations (run from /backend)
python -m alembic upgrade head

# Check current migration state
python -m alembic current

# Generate a new migration after model changes
python -m alembic revision --autogenerate -m "describe_your_change"

# Rollback one migration
python -m alembic downgrade -1
```

Migration files live in `backend/alembic/versions/`. Always review auto-generated migrations before applying.

---

## Production Checklist

- [ ] `DATABASE_URL` points to Neon (not localhost)
- [ ] `BACKEND_CORS_ORIGINS` set to your Vercel URL
- [ ] `NEXT_PUBLIC_BACKEND_URL` set to your Render URL
- [ ] Clerk production instance keys configured
- [ ] UploadThing app configured with your production domain
- [ ] `alembic upgrade head` run against Neon
- [ ] `/health` endpoint returns `200 OK`
- [ ] Full pipeline smoke test: upload → run pipeline → download MP4
- [ ] `MOTIONFORGE_AUTH_BYPASS` is `false` (or unset)

---

## License

MIT
