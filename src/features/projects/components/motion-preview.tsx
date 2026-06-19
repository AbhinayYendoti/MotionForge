"use client";

import { Player } from "@remotion/player";
import { MotionForgeVideo } from "@/remotion/Video";
import type { LayerExtraction, MotionPlan, Storyboard, VisualAnalysis } from "@/remotion/types";

type Props = {
  imageUrl: string;
  storyboard: Storyboard;
  motionPlan: MotionPlan;
  layers: LayerExtraction;
  analysis: VisualAnalysis | null;
  format?: "reel" | "landscape" | "square";
};

const FORMATS = {
  reel:      { width: 1080, height: 1920 },
  landscape: { width: 1920, height: 1080 },
  square:    { width: 1080, height: 1080 },
} as const;

export function MotionPreview({ imageUrl, storyboard, motionPlan, layers, analysis, format = "reel" }: Props) {
  const { width, height } = FORMATS[format] ?? FORMATS.reel;
  const durationInFrames = Math.max(30, Math.ceil(storyboard.totalDurationSeconds * 30));

  const inputProps = { imageUrl, storyboard, motionPlan, layers, analysis, width, height };

  // Render at half resolution for performance in the browser
  const previewScale = format === "landscape" ? 0.36 : 0.28;

  return (
    <div className="flex flex-col items-center gap-4">
      <div
        style={{
          width:  Math.round(width  * previewScale),
          height: Math.round(height * previewScale),
          borderRadius: 16,
          overflow: "hidden",
          boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
        }}
      >
        <Player
          component={MotionForgeVideo}
          inputProps={inputProps}
          durationInFrames={durationInFrames}
          fps={30}
          compositionWidth={width}
          compositionHeight={height}
          style={{ width: "100%", height: "100%" }}
          controls
          loop
          autoPlay
          showVolumeControls={false}
          clickToPlay
          doubleClickToFullscreen
        />
      </div>
      <p className="text-[13px] font-[450] text-muted-foreground">
        Live preview — {format} · {width}×{height} · {storyboard.totalDurationSeconds}s
      </p>
    </div>
  );
}
