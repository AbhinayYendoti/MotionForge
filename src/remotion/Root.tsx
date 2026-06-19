import { Composition } from "remotion";
import { MotionForgeVideo } from "./Video";

export function RemotionRoot() {
  return (
    <Composition
      id="MotionForgeVideo"
      component={MotionForgeVideo}
      durationInFrames={300}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        imageUrl: "/uploads/example.png",
        width: 1080,
        height: 1920,
        analysis: {
          product: "Premium Product",
          brand: "MotionForge",
          colors: ["#7c3aed", "#3b82f6"],
          detectedText: ["MotionForge", "Premium"],
          style: "Modern minimal marketing",
          composition: {
            focalPoint: "Center of frame",
            hierarchy: ["Product", "Headline", "CTA"],
            layout: "centered",
          },
          productCategory: "Technology",
        },
        storyboard: {
          title: "MotionForge Campaign",
          totalDurationSeconds: 10,
          scenes: [
            {
              id: "scene-1",
              name: "Product Reveal",
              objective: "Reveal the product with a premium entrance",
              durationSeconds: 4,
              narration: "A premium product reveal crafted with intelligence.",
              onScreenText: "Designed to Move",
            },
            {
              id: "scene-2",
              name: "Call To Action",
              objective: "Drive viewer action",
              durationSeconds: 6,
              narration: "Experience AI-powered motion at its finest.",
              onScreenText: "MotionForge",
            },
          ],
        },
        motionPlan: {
          format: "reel",
          fps: 30,
          animations: [
            {
              sceneId: "scene-1",
              layerId: "background",
              fromFrame: 0,
              toFrame: 120,
              transform: { scale: [1.0, 1.08], translateY: [0, -20], opacity: [0.7, 0.9] },
              easing: "easeOut",
            },
            {
              sceneId: "scene-1",
              layerId: "product-primary",
              fromFrame: 0,
              toFrame: 90,
              transform: { translateY: [60, 0], scale: [0.92, 1.0], opacity: [0, 1] },
              easing: "easeOut",
            },
            {
              sceneId: "scene-2",
              layerId: "product-primary",
              fromFrame: 120,
              toFrame: 240,
              transform: { scale: [1.0, 1.06], translateX: [0, -15] },
              easing: "easeInOut",
            },
            {
              sceneId: "scene-2",
              layerId: "background",
              fromFrame: 120,
              toFrame: 300,
              transform: { scale: [1.04, 1.12], translateY: [-10, -30] },
              easing: "easeIn",
            },
          ],
        },
        layers: {
          image: { width: 1080, height: 1920 },
          layers: [
            {
              id: "background",
              type: "background",
              label: "Background plate",
              bounds: { x: 0, y: 0, width: 1080, height: 1920 },
              confidence: 1,
            },
            {
              id: "product-primary",
              type: "product",
              label: "Primary product region",
              bounds: { x: 194, y: 346, width: 692, height: 1114 },
              confidence: 0.85,
            },
          ],
        },
      }}
    />
  );
}
