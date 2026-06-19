import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { ProjectCreateForm } from "@/features/projects/components/project-create-form";
import { ColorBlock } from "@/components/ui/color-block";
import { SiteNav } from "@/components/layout/site-nav";

export default function NewProjectPage() {
  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-page px-6 pb-20 pt-32">
      <Link href="/dashboard" className="mb-10 inline-flex items-center rounded-pill px-4 py-2 text-[16px] font-[500] tracking-[-0.02em]">
        <ArrowLeft className="mr-2 h-5 w-5" /> Dashboard
      </Link>
      <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr]">
        <ColorBlock variant="cream" className="min-h-[520px]">
          <p className="eyebrow mb-8">New project</p>
          <h1 className="display-lg">Upload a creative and define the motion campaign.</h1>
          <p className="mt-8 text-[20px] font-[450] leading-[1.4] text-muted-foreground">
            MotionForge will keep the pipeline visible from upload through final render.
          </p>
          <div className="mt-14 aspect-square max-w-[280px] rounded-full bg-card shadow-soft" />
        </ColorBlock>
        <section className="rounded-hero border border-border bg-card p-6 text-card-foreground shadow-nav md:p-10">
          <ProjectCreateForm />
        </section>
      </div>
      </main>
    </>
  );
}
