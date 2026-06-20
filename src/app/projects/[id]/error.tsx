"use client";

import { useEffect } from "react";
import { AlertCircle } from "lucide-react";
import { SiteNav } from "@/components/layout/site-nav";
import { LinkButton } from "@/components/ui/link-button";

export default function ProjectError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-page px-6 pb-20 pt-32">
        <div className="flex min-h-[40vh] flex-col items-center justify-center text-center">
          <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10 text-destructive">
            <AlertCircle className="h-8 w-8" />
          </div>
          <h1 className="mb-4 text-2xl font-semibold tracking-tight">Something went wrong</h1>
          <p className="mb-8 max-w-md text-muted-foreground">
            {error.message || "We couldn't load this project. It may have been deleted or the server might be temporarily unavailable."}
          </p>
          <div className="flex gap-4">
            <button onClick={() => reset()} className="inline-flex h-10 items-center justify-center rounded-full bg-secondary px-6 text-sm font-medium transition-colors hover:bg-secondary/80">
              Try again
            </button>
            <LinkButton href="/dashboard" className="h-10 px-6">
              Go to Dashboard
            </LinkButton>
          </div>
        </div>
      </main>
    </>
  );
}
