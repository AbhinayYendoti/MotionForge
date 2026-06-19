import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Download } from "lucide-react";
import { requireUser } from "@/lib/auth";
import { getProject } from "@/lib/backend";
import { PipelineRail } from "@/features/projects/components/pipeline-rail";
import { ProjectAutoRefresh } from "@/features/projects/components/project-auto-refresh";
import { RunPipelineForm } from "@/features/projects/components/run-pipeline-form";
import { JsonPanel } from "@/features/projects/components/json-panel";
import { Badge } from "@/components/ui/badge";
import { LinkButton } from "@/components/ui/link-button";
import { SiteNav } from "@/components/layout/site-nav";
import type { LayerExtraction, MotionPlan, Storyboard, VisualAnalysis } from "@/remotion/types";

import { MotionPreviewLoader } from "@/features/projects/components/motion-preview-loader";

export default async function ProjectPage({ params }: { params: Promise<{ id: string }> }) {
  await requireUser();
  const { id } = await params;
  const project = await getProject(id).catch(() => null);
  if (!project) notFound();

  const latestRender = project.renders[0];

  // Resolve pipeline data for the preview player
  const storyboardJson  = project.storyboard?.storyboardJson  as Storyboard | undefined;
  const motionPlanJson  = project.motionPlan?.motionPlanJson  as MotionPlan  | undefined;
  const layerDataJson   = project.layerData?.layersJson       as LayerExtraction | undefined;
  const analysisJson    = project.analysis?.analysisJson      as VisualAnalysis  | undefined;
  const uploadImageUrl  = project.upload?.imageUrl ?? null;

  const canShowPreview =
    uploadImageUrl &&
    storyboardJson &&
    motionPlanJson &&
    layerDataJson;

  // Infer render format from the latest render or fall back to "reel"
  const renderFormat = (latestRender?.format ?? "reel") as "reel" | "landscape" | "square";

  return (
    <>
      <ProjectAutoRefresh status={project.status} />
      <SiteNav />
      <main className="mx-auto max-w-page px-6 pb-20 pt-32">
        <Link href="/dashboard" className="mb-10 inline-flex items-center rounded-pill px-4 py-2 text-[16px] font-[500] tracking-[-0.02em]">
          <ArrowLeft className="mr-2 h-5 w-5" /> Dashboard
        </Link>

        <section className="mb-10 grid gap-8 lg:grid-cols-[0.85fr_1.15fr]">
          <div className="relative mx-auto aspect-square w-full max-w-[520px] overflow-hidden rounded-full bg-card shadow-soft">
            {project.upload?.imageUrl ? (
              <Image src={project.upload.imageUrl} alt={project.title} fill className="object-cover" sizes="(max-width: 1024px) 100vw, 480px" />
            ) : null}
            <div className="absolute bottom-8 right-8 flex h-16 w-16 items-center justify-center rounded-full bg-card text-foreground shadow-nav">
              <Download size={22} />
            </div>
          </div>
          <div className="flex flex-col justify-between rounded-hero bg-secondary p-8 text-secondary-foreground shadow-soft md:p-12">
            <div>
              <div className="mb-6 flex flex-wrap gap-3">
                <Badge>{project.status.toLowerCase()}</Badge>
                {latestRender ? <Badge>{latestRender.renderStatus.toLowerCase()}</Badge> : null}
              </div>
              <h1 className="display-lg">{project.title}</h1>
              <p className="mt-6 max-w-2xl text-[18px] font-[450] leading-[1.4] text-muted-foreground">
                {project.prompt || "No creative direction provided."}
              </p>
              {project.error ? (
                <p className="mt-6 rounded-[24px] bg-card p-4 text-[16px] font-[450] text-card-foreground">{project.error}</p>
              ) : null}
            </div>
            <div className="mt-10 flex flex-col gap-4">
              <RunPipelineForm projectId={project.id} />
              {latestRender?.videoUrl ? (
                <LinkButton href={latestRender.videoUrl} variant="secondary" size="lg" download>
                  <Download className="mr-2 h-5 w-5" /> Download MP4
                </LinkButton>
              ) : null}
            </div>
          </div>
        </section>

        {/* Pipeline progress rail */}
        <section className="mb-10 rounded-hero border border-border bg-secondary p-6 text-secondary-foreground shadow-nav">
          <p className="eyebrow mb-6">Pipeline</p>
          <PipelineRail steps={project.pipeline.map((step) => ({ id: step.id, label: step.label, status: step.status }))} />
        </section>

        {/* In-browser motion preview (appears once storyboard + motion plan are ready) */}
        {canShowPreview && (
          <section className="mb-10 rounded-hero bg-secondary p-6 text-secondary-foreground shadow-soft md:p-10">
            <p className="eyebrow mb-6">Motion preview</p>
            <div className="flex justify-center">
              <MotionPreviewLoader
                imageUrl={uploadImageUrl}
                storyboard={storyboardJson!}
                motionPlan={motionPlanJson!}
                layers={layerDataJson!}
                analysis={analysisJson ?? null}
                format={renderFormat}
              />
            </div>
          </section>
        )}

        {/* Rendered MP4 video */}
        {latestRender?.videoUrl ? (
          <section className="mb-10 rounded-hero bg-secondary p-6 text-secondary-foreground shadow-soft md:p-10">
            <p className="eyebrow mb-6">Generated video</p>
            <video
              src={latestRender.videoUrl}
              controls
              className="mx-auto max-h-[720px] w-full rounded-hero bg-primary"
            />
            {latestRender.logs ? (
              <p className="mt-5 text-[16px] font-[450] text-muted-foreground">{latestRender.logs}</p>
            ) : null}
          </section>
        ) : null}

        {/* JSON debug panels */}
        <section className="grid gap-6 lg:grid-cols-2">
          <JsonPanel title="Visual understanding" value={project.analysis?.analysisJson} />
          <JsonPanel title="OCR" value={project.ocrResult?.ocrJson} />
          <JsonPanel title="Layer extraction" value={project.layerData?.layersJson} />
          <JsonPanel title="Storyboard" value={project.storyboard?.storyboardJson} />
          <JsonPanel title="Motion plan" value={project.motionPlan?.motionPlanJson} />
          <JsonPanel title="Evaluation" value={project.evaluation?.evaluationJson} />
          <JsonPanel title="Render logs" value={latestRender?.logs ? { logs: latestRender.logs } : null} />
        </section>
      </main>
    </>
  );
}
