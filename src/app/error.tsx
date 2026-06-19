"use client";

import { Button } from "@/components/ui/button";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <section className="max-w-xl rounded-hero bg-secondary p-12 text-secondary-foreground shadow-soft">
        <p className="eyebrow mb-6">System notice</p>
        <h1 className="display-lg mb-6">Something needs attention.</h1>
        <p className="mb-8 text-[18px] font-[450] leading-[1.4] text-muted-foreground">{error.message}</p>
        <Button onClick={reset}>Try again</Button>
      </section>
    </main>
  );
}
