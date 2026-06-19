from typing import Literal

from pydantic import BaseModel, Field


class Bounds(BaseModel):
    x: float
    y: float
    width: float
    height: float


class VisualComposition(BaseModel):
    focalPoint: str
    hierarchy: list[str]
    layout: str


class VisualAnalysis(BaseModel):
    product: str
    brand: str | None
    colors: list[str] = Field(min_length=1)
    detectedText: list[str]
    style: str
    composition: VisualComposition
    productCategory: str


class OcrWord(BaseModel):
    text: str
    confidence: float = Field(ge=0, le=1)
    bounds: Bounds


class OcrImage(BaseModel):
    width: int
    height: int


class OcrResult(BaseModel):
    image: OcrImage
    text: str
    words: list[OcrWord]
    warning: str | None = None


class Layer(BaseModel):
    id: str
    type: Literal["background", "product", "logo", "text", "accent"]
    label: str
    bounds: Bounds
    confidence: float = Field(ge=0, le=1)
    text: str | None = None


class LayerExtraction(BaseModel):
    image: OcrImage
    layers: list[Layer] = Field(min_length=1)


class Scene(BaseModel):
    id: str
    name: str
    objective: str
    durationSeconds: float = Field(ge=1, le=10)
    narration: str
    onScreenText: str | None = None


class Storyboard(BaseModel):
    title: str
    totalDurationSeconds: float = Field(ge=3, le=30)
    scenes: list[Scene] = Field(min_length=2, max_length=6)


class Transform(BaseModel):
    translateX: tuple[float, float] | None = None
    translateY: tuple[float, float] | None = None
    scale: tuple[float, float] | None = None
    opacity: tuple[float, float] | None = None
    rotate: tuple[float, float] | None = None


class Animation(BaseModel):
    sceneId: str
    layerId: str
    fromFrame: int = Field(ge=0)
    toFrame: int = Field(ge=1)
    transform: Transform
    easing: Literal["linear", "easeIn", "easeOut", "easeInOut"] = "easeOut"


class MotionPlan(BaseModel):
    format: Literal["reel", "landscape", "square"] = "reel"
    fps: int = 30
    animations: list[Animation]


class EvaluationCheck(BaseModel):
    name: str
    passed: bool
    notes: str


class Evaluation(BaseModel):
    approved: bool
    score: float = Field(ge=0, le=100)
    checks: list[EvaluationCheck]
    regenerationReasons: list[str] = Field(default_factory=list)

