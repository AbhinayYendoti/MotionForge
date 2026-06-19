import { Plus } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { requireUser } from "@/lib/auth";
import { getDashboard } from "@/lib/backend";
import { LinkButton } from "@/components/ui/link-button";
import { Badge } from "@/components/ui/badge";
import { SiteNav } from "@/components/layout/site-nav";

function statusLabel(status: string) {
  return status.toLowerCase().replace(/_/g, " ");
}

export default async function DashboardPage() {
  await requireUser();
  const { projects, renderCount, completedCount } = await getDashboard();

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-page px-6 pb-20 pt-32">
      <div className="mb-16 flex flex-col justify-between gap-8 md:flex-row md:items-end">
        <div>
          <p className="eyebrow mb-5">Dashboard</p>
          <h1 className="display-lg">Motion campaigns.</h1>
          <p className="mt-5 max-w-2xl text-[18px] font-[450] leading-[1.4] text-muted-foreground">
            Create, inspect, and render campaigns through the MotionForge pipeline.
          </p>
        </div>
        <LinkButton href="/projects/new" size="lg">
          <Plus className="mr-2 h-5 w-5" /> New project
        </LinkButton>
      </div>

      <section className="mb-12 grid gap-5 md:grid-cols-3">
        {[
          ["Recent Projects", projects.length],
          ["Created Videos", renderCount],
          ["Completed", completedCount]
        ].map(([label, value]) => (
          <div key={label} className="rounded-hero border border-border bg-card p-8 text-card-foreground shadow-nav">
            <p className="eyebrow mb-8">{label}</p>
            <p className="text-[64px] font-[500] leading-none tracking-[-0.02em]">{value}</p>
          </div>
        ))}
      </section>

      <section className="rounded-hero bg-secondary p-6 text-secondary-foreground shadow-soft md:p-10">
        <div className="mb-8 flex items-center justify-between gap-4">
          <h2 className="text-[32px] font-[500] tracking-[-0.02em]">Recent projects</h2>
          <Badge>{projects.length} total</Badge>
        </div>
        <div className="grid gap-4">
          {projects.length === 0 ? (
            <div className="rounded-[32px] bg-card p-8 text-card-foreground">
              <p className="text-[18px] font-[450]">Create your first project to run the MotionForge pipeline.</p>
            </div>
          ) : null}
          {projects.map((project) => (
            <Link key={project.id} href={`/projects/${project.id}`} className="grid gap-5 rounded-[36px] bg-card p-4 text-card-foreground transition-transform duration-150 hover:-translate-y-1 md:grid-cols-[112px_1fr_auto] md:items-center">
              <div className="relative aspect-square overflow-hidden rounded-full bg-background">
                {project.upload?.imageUrl ? (
                  <Image src={project.upload.imageUrl} alt="" fill className="object-cover" sizes="96px" />
                ) : null}
              </div>
              <div>
                <h3 className="text-[24px] font-[500] leading-[1.2] tracking-[-0.02em]">{project.title}</h3>
                <p className="mt-2 text-[16px] font-[450] leading-[1.4] text-muted-foreground">{project.prompt || "No prompt provided"}</p>
              </div>
              <Badge className="justify-self-start md:justify-self-end">{statusLabel(project.status)}</Badge>
            </Link>
          ))}
        </div>
      </section>
      </main>
    </>
  );
}
