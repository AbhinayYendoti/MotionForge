"use client";

import dynamic from "next/dynamic";
import type { LayerExtraction, MotionPlan, Storyboard, VisualAnalysis } from "@/remotion/types";

// dynamic() with ssr:false MUST live inside a Client Component — not a Server Component
const MotionPreviewInner = dynamic(
  () => import("./motion-preview").then((m) => m.MotionPreview),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-48 items-center justify-center rounded-hero bg-card text-[15px] text-muted-foreground">
        Loading preview…
      </div>
    ),
  }
);

type Props = {
  imageUrl: string;
  storyboard: Storyboard;
  motionPlan: MotionPlan;
  layers: LayerExtraction;
  analysis: VisualAnalysis | null;
  format?: "reel" | "landscape" | "square";
};

export function MotionPreviewLoader(props: Props) {
  return <MotionPreviewInner {...props} />;
}
