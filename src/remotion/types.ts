export type VisualAnalysis = {
  product: string;
  brand: string | null;
  colors: string[];
  detectedText: string[];
  style: string;
  composition: {
    focalPoint: string;
    hierarchy: string[];
    layout: string;
  };
  productCategory: string;
};

export type Storyboard = {
  title: string;
  totalDurationSeconds: number;
  scenes: Array<{
    id: string;
    name: string;
    objective: string;
    durationSeconds: number;
    narration: string;
    onScreenText?: string;
  }>;
};

export type MotionPlan = {
  format: "reel" | "landscape" | "square";
  fps: number;
  animations: Array<{
    sceneId: string;
    layerId: string;
    fromFrame: number;
    toFrame: number;
    transform: {
      translateX?: [number, number];
      translateY?: [number, number];
      scale?: [number, number];
      opacity?: [number, number];
      rotate?: [number, number];
    };
    easing: "linear" | "easeIn" | "easeOut" | "easeInOut";
  }>;
};

export type LayerExtraction = {
  image: { width: number; height: number };
  layers: Array<{
    id: string;
    type: "background" | "product" | "logo" | "text" | "accent";
    label: string;
    bounds: { x: number; y: number; width: number; height: number };
    confidence: number;
    text?: string;
  }>;
};
