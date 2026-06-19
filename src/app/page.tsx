import { ArrowRight, Check, Film, Layers3, Sparkles, type LucideIcon } from "lucide-react";
import { Footer } from "@/components/layout/footer";
import { SiteNav } from "@/components/layout/site-nav";
import { LinkButton } from "@/components/ui/link-button";
import { Reveal } from "@/components/ui/reveal";

const pipeline = ["Upload", "Analysis", "OCR", "Layer Extraction", "Storyboard", "Motion Planning", "Evaluation", "Rendering", "Completed"];

const featureCards: Array<{ title: string; copy: string; icon: LucideIcon; eyebrow: string }> = [
  {
    title: "Visual understanding",
    copy: "Detect product, typography, hierarchy, style, dominant colors, and campaign intent before motion is planned.",
    icon: Layers3,
    eyebrow: "Services"
  },
  {
    title: "Directed motion",
    copy: "Generate structured animation JSON for camera moves, fades, zooms, text reveals, and CTA pacing.",
    icon: Sparkles,
    eyebrow: "Solutions"
  },
  {
    title: "Rendered output",
    copy: "Orchestrate Remotion renders for reels, landscape videos, and square social campaigns with status tracking.",
    icon: Film,
    eyebrow: "Rendering"
  }
];

function MastercardMark() {
  return (
    <span className="relative inline-flex h-12 w-16 align-middle">
      <span className="absolute left-0 top-2 h-10 w-10 rounded-full bg-mc-red" />
      <span className="absolute left-6 top-2 h-10 w-10 rounded-full bg-mc-yellow mix-blend-multiply" />
    </span>
  );
}

function PipelineOrbit() {
  return (
    <div className="relative mx-auto max-w-5xl py-12">
      <div className="orbital-arc left-6 top-10 hidden h-44 w-[42%] rotate-3 md:block" />
      <div className="orbital-arc right-8 top-24 hidden h-56 w-[48%] -rotate-6 md:block" />
      <div className="grid gap-4 md:grid-cols-3">
        {pipeline.map((step, index) => (
          <div
            key={step}
            className="relative rounded-pill border border-border bg-card px-5 py-4 text-card-foreground shadow-nav"
            style={{ marginTop: index % 3 === 1 ? 32 : index % 3 === 2 ? 8 : 0 }}
          >
            <div className="flex items-center gap-4">
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
                <Check size={16} />
              </span>
              <div>
                <p className="text-[16px] font-[500] leading-tight tracking-[-0.02em]">{step}</p>
                <p className="mt-1 text-[13px] font-[450] text-muted-foreground">Stage {String(index + 1).padStart(2, "0")}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function HomePage() {
  return (
    <>
      <SiteNav />
      <main className="overflow-hidden pt-28">
        <section className="mx-auto max-w-page px-6 pb-16 pt-16 md:pb-24 md:pt-24">
          <Reveal>
            <p className="eyebrow mb-8">MotionForge</p>
            <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
              <h1 className="display-xl max-w-4xl">Turn static creatives into motion campaigns.</h1>
              <div>
                <p className="max-w-xl text-[18px] font-[450] leading-[1.4] text-muted-foreground">
                  Upload a product image, poster, or ad creative. MotionForge decomposes the layout, plans the story, directs the motion, evaluates quality, and renders an MP4.
                </p>
                <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                  <LinkButton href="/dashboard" size="lg">
                    Get started <ArrowRight className="ml-2 h-5 w-5" />
                  </LinkButton>
                  <LinkButton href="#pipeline" variant="secondary" size="lg">
                    See pipeline
                  </LinkButton>
                </div>
              </div>
            </div>
          </Reveal>
        </section>

        <Reveal className="mx-auto max-w-[1500px] px-6">
          <section className="relative min-h-[520px] overflow-hidden rounded-hero bg-footer p-8 text-footer-foreground shadow-soft md:p-12">
            <div className="absolute right-10 top-10 hidden text-[120px] font-[500] leading-none tracking-[-0.02em] text-footer-foreground/10 md:block">
              Motion
            </div>
            <div className="relative z-10 flex h-full min-h-[456px] flex-col justify-between">
              <div className="flex items-center justify-between gap-4">
                <p className="eyebrow text-footer-foreground">Campaign render</p>
                <div className="rounded-pill border border-footer-foreground/35 px-5 py-3 text-[14px] font-[500]">1080 x 1920</div>
              </div>
              <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-end">
                <div>
                  <MastercardMark />
                  <h2 className="mt-8 max-w-xl text-[48px] font-[500] leading-none tracking-[-0.02em] md:text-[72px]">Product reveal, directed frame by frame.</h2>
                </div>
                <div className="rounded-[40px] bg-background p-6 text-foreground">
                  <div className="grid gap-4 md:grid-cols-3">
                    {["Scene 01", "Scene 02", "Scene 03"].map((scene, index) => (
                      <div key={scene} className="rounded-[32px] bg-card p-5 text-card-foreground">
                        <p className="text-[13px] font-[700] uppercase tracking-[0.04em] text-muted-foreground">{scene}</p>
                        <p className="mt-12 text-[24px] font-[500] leading-[1.2] tracking-[-0.02em]">
                          {index === 0 ? "Reveal" : index === 1 ? "Highlight" : "Call to action"}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </Reveal>

        <section id="pipeline" className="mx-auto max-w-page px-6 py-24 md:py-32">
          <Reveal>
            <div className="relative">
              <p className="absolute -top-10 left-0 hidden text-[128px] font-[500] leading-none tracking-[-0.02em] text-ghost-cream md:block">
                Pipeline
              </p>
              <div className="relative z-10 grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
                <div>
                  <p className="eyebrow mb-6">Explainable generation</p>
                  <h2 className="display-lg">A production pipeline users can actually inspect.</h2>
                </div>
                <p className="text-[18px] font-[450] leading-[1.4] text-muted-foreground">
                  The system shows every stage, from upload and OCR to final render. It is not a black-box video generator; it is a controllable motion campaign pipeline.
                </p>
              </div>
            </div>
          </Reveal>
          <Reveal>
            <PipelineOrbit />
          </Reveal>
        </section>

        <section id="rendering" className="mx-auto max-w-page px-6 py-16 md:py-24">
          <Reveal>
            <div className="grid gap-12 lg:grid-cols-3">
              {featureCards.map(({ title, copy, icon: Icon, eyebrow }, index) => (
                <article key={title} className="relative">
                  <div className="relative mx-auto flex aspect-square max-w-[320px] items-center justify-center rounded-full bg-card text-card-foreground shadow-soft">
                    <div className="orbital-arc -left-16 top-1/2 hidden h-28 w-56 -translate-y-1/2 rotate-6 md:block" />
                    <Icon className="h-16 w-16 text-primary" strokeWidth={1.5} />
                    <LinkButton href="/dashboard" size="icon" variant="secondary" className="absolute -bottom-2 right-8 h-14 w-14 border-0 shadow-nav" aria-label={`Open ${title}`}>
                      <ArrowRight className="h-5 w-5" />
                    </LinkButton>
                  </div>
                  <div className={index === 1 ? "mt-10 lg:mt-16" : "mt-10"}>
                    <p className="eyebrow mb-4">{eyebrow}</p>
                    <h3 className="max-w-sm text-[24px] font-[500] leading-[1.2] tracking-[-0.02em]">{title}</h3>
                    <p className="mt-4 max-w-sm text-[16px] font-[450] leading-[1.4] text-muted-foreground">{copy}</p>
                  </div>
                </article>
              ))}
            </div>
          </Reveal>
        </section>

        <section id="quality" className="mx-auto max-w-page px-6 py-20 md:py-32">
          <Reveal>
            <div className="relative overflow-hidden rounded-hero bg-secondary p-8 text-secondary-foreground shadow-soft md:p-14">
              <p className="eyebrow mb-8">Quality gate</p>
              <div className="grid gap-10 lg:grid-cols-[1fr_0.8fr] lg:items-end">
                <h2 className="display-lg max-w-3xl">Every render is checked before it becomes a deliverable.</h2>
                <p className="text-[18px] font-[450] leading-[1.4] text-muted-foreground">
                  The evaluation agent scores text visibility, branding consistency, animation smoothness, scene pacing, and composition quality before rendering.
                </p>
              </div>
            </div>
          </Reveal>
        </section>
      </main>
      <Footer />
    </>
  );
}
