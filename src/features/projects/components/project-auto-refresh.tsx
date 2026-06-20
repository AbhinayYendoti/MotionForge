"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

const ACTIVE_STATUSES = new Set(["ANALYZING", "EXTRACTING", "STORYBOARDING", "PLANNING", "EVALUATING", "RENDERING"]);

export function ProjectAutoRefresh({ status }: { status: string }) {
  const router = useRouter();

  useEffect(() => {
    if (!ACTIVE_STATUSES.has(status)) return;
    const interval = window.setInterval(() => router.refresh(), 4000);
    // Stop polling after 5 minutes to prevent infinite loops if backend hangs
    const timeout = window.setTimeout(() => window.clearInterval(interval), 5 * 60 * 1000);
    return () => {
      window.clearInterval(interval);
      window.clearTimeout(timeout);
    };
  }, [router, status]);

  return null;
}
