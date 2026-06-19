"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

const ACTIVE_STATUSES = new Set(["ANALYZING", "EXTRACTING", "STORYBOARDING", "PLANNING", "EVALUATING", "RENDERING"]);

export function ProjectAutoRefresh({ status }: { status: string }) {
  const router = useRouter();

  useEffect(() => {
    if (!ACTIVE_STATUSES.has(status)) return;
    const interval = window.setInterval(() => router.refresh(), 4000);
    return () => window.clearInterval(interval);
  }, [router, status]);

  return null;
}
