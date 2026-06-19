export const pipelineSteps = [
  { key: "upload", label: "Upload" },
  { key: "analysis", label: "Analysis" },
  { key: "ocr", label: "OCR" },
  { key: "layers", label: "Layer Extraction" },
  { key: "storyboard", label: "Storyboard" },
  { key: "motion", label: "Motion Planning" },
  { key: "evaluation", label: "Evaluation" },
  { key: "rendering", label: "Rendering" },
  { key: "completed", label: "Completed" }
] as const;
