import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { LayerExtraction, MotionPlan, Storyboard, VisualAnalysis } from "./types";

// ─── Props ─────────────────────────────────────────────────────────────────────

export type MotionForgeVideoProps = {
  imageUrl: string;
  storyboard: Storyboard;
  motionPlan: MotionPlan;
  layers: LayerExtraction;
  analysis: VisualAnalysis | null;
  width: number;
  height: number;
};

// ─── Constants ─────────────────────────────────────────────────────────────────

const TRANSITION_FRAMES = 10;

// ─── Helpers ───────────────────────────────────────────────────────────────────

function sceneAtFrame(storyboard: Storyboard, frame: number, fps: number) {
  let cursor = 0;
  for (let i = 0; i < storyboard.scenes.length; i++) {
    const scene = storyboard.scenes[i];
    const start = cursor;
    const end = cursor + scene.durationSeconds * fps;
    if (frame >= start && frame < end) return { scene, start, end, index: i };
    cursor = end;
  }
  const last = storyboard.scenes[storyboard.scenes.length - 1];
  const i = storyboard.scenes.length - 1;
  const start = Math.max(0, cursor - last.durationSeconds * fps);
  return { scene: last, start, end: cursor, index: i };
}

function getEasingFn(easing: string): (t: number) => number {
  switch (easing) {
    case "easeIn":    return Easing.in(Easing.quad);
    case "easeOut":   return Easing.out(Easing.quad);
    case "easeInOut": return Easing.inOut(Easing.quad);
    default:          return Easing.linear;
  }
}

/**
 * Compute CSS style from motionPlan animations for a given layerId at the current frame.
 * Falls back to the start/end state of adjacent animations when the frame is outside
 * any active animation window.
 */
function getLayerStyle(
  motionPlan: MotionPlan,
  layerId: string,
  frame: number
): React.CSSProperties {
  const allForLayer = motionPlan.animations.filter((a) => a.layerId === layerId);

  // Active animations — frame is within [fromFrame, toFrame]
  const active = allForLayer.filter(
    (a) => frame >= a.fromFrame && frame <= a.toFrame
  );

  if (active.length === 0) {
    // Clamp to end state of the most recent past animation
    const past = allForLayer
      .filter((a) => frame > a.toFrame)
      .sort((a, b) => b.toFrame - a.toFrame);
    if (past.length > 0) return endState(past[0]);

    // Clamp to start state of the nearest upcoming animation
    const future = allForLayer
      .filter((a) => frame < a.fromFrame)
      .sort((a, b) => a.fromFrame - b.fromFrame);
    if (future.length > 0) return startState(future[0]);

    return {};
  }

  // Merge all active animations
  const style: React.CSSProperties = {};
  const transforms: string[] = [];

  for (const anim of active) {
    const { transform, fromFrame, toFrame, easing } = anim;
    const easeFn = getEasingFn(easing);
    const safeFrom = Math.min(fromFrame, toFrame - 1);
    const safeTo   = Math.max(toFrame, fromFrame + 1);

    if (transform.translateX != null) {
      const v = interpolate(frame, [safeFrom, safeTo], transform.translateX, {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeFn,
      });
      transforms.push(`translateX(${v}px)`);
    }
    if (transform.translateY != null) {
      const v = interpolate(frame, [safeFrom, safeTo], transform.translateY, {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeFn,
      });
      transforms.push(`translateY(${v}px)`);
    }
    if (transform.scale != null) {
      const v = interpolate(frame, [safeFrom, safeTo], transform.scale, {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeFn,
      });
      transforms.push(`scale(${v})`);
    }
    if (transform.rotate != null) {
      const v = interpolate(frame, [safeFrom, safeTo], transform.rotate, {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeFn,
      });
      transforms.push(`rotate(${v}deg)`);
    }
    if (transform.opacity != null) {
      style.opacity = interpolate(frame, [safeFrom, safeTo], transform.opacity, {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeFn,
      });
    }
  }

  if (transforms.length > 0) style.transform = transforms.join(" ");
  return style;
}

function endState(
  anim: MotionPlan["animations"][number]
): React.CSSProperties {
  const style: React.CSSProperties = {};
  const transforms: string[] = [];
  const t = anim.transform;
  if (t.translateX) transforms.push(`translateX(${t.translateX[1]}px)`);
  if (t.translateY) transforms.push(`translateY(${t.translateY[1]}px)`);
  if (t.scale)      transforms.push(`scale(${t.scale[1]})`);
  if (t.rotate)     transforms.push(`rotate(${t.rotate[1]}deg)`);
  if (t.opacity != null) style.opacity = t.opacity[1];
  if (transforms.length > 0) style.transform = transforms.join(" ");
  return style;
}

function startState(
  anim: MotionPlan["animations"][number]
): React.CSSProperties {
  const style: React.CSSProperties = {};
  const transforms: string[] = [];
  const t = anim.transform;
  if (t.translateX) transforms.push(`translateX(${t.translateX[0]}px)`);
  if (t.translateY) transforms.push(`translateY(${t.translateY[0]}px)`);
  if (t.scale)      transforms.push(`scale(${t.scale[0]})`);
  if (t.rotate)     transforms.push(`rotate(${t.rotate[0]}deg)`);
  if (t.opacity != null) style.opacity = t.opacity[0];
  if (transforms.length > 0) style.transform = transforms.join(" ");
  return style;
}

/** Whether motionPlan defines ANY animation for this layerId */
function hasAnimations(motionPlan: MotionPlan, layerId: string): boolean {
  return motionPlan.animations.some((a) => a.layerId === layerId);
}

// ─── Component ─────────────────────────────────────────────────────────────────

export function MotionForgeVideo({
  imageUrl,
  storyboard,
  motionPlan,
  layers,
  analysis,
  width,
  height,
}: MotionForgeVideoProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ── Scene state ────────────────────────────────────────────────────────────
  const { scene, start: sceneStart, end: sceneEnd, index: sceneIndex } =
    sceneAtFrame(storyboard, frame, fps);
  const isLastScene = sceneIndex === storyboard.scenes.length - 1;
  const framesIntoScene = frame - sceneStart;
  const framesUntilEnd  = sceneEnd - frame;
  const totalFrames     = Math.max(1, storyboard.totalDurationSeconds * fps);

  // ── Scene transition opacity (fade-through-black) ─────────────────────────
  const entranceOpacity = Math.min(1, framesIntoScene / TRANSITION_FRAMES);
  const exitOpacity     = isLastScene ? 1 : Math.min(1, framesUntilEnd / TRANSITION_FRAMES);
  const sceneOpacity    = Math.min(entranceOpacity, exitOpacity);
  const overlayOpacity  = 1 - sceneOpacity; // black overlay fades out as content fades in

  // ── Brand colours ──────────────────────────────────────────────────────────
  const brandColor  = analysis?.colors?.[0] ?? "#7c3aed";
  const accentColor = analysis?.colors?.[1] ?? brandColor;

  // ── Image URL ──────────────────────────────────────────────────────────────
  const safeImageUrl = imageUrl.startsWith("/")
    ? staticFile(imageUrl.slice(1))
    : imageUrl;

  // ── Layer scale factors (map source-image pixels → video pixels) ───────────
  const imgW  = layers.image.width  > 0 ? layers.image.width  : width;
  const imgH  = layers.image.height > 0 ? layers.image.height : height;
  const scaleX = width  / imgW;
  const scaleY = height / imgH;

  // ── Identify structural layers ─────────────────────────────────────────────
  const bgLayer      = layers.layers.find((l) => l.type === "background");
  const productLayer = layers.layers.find((l) => l.type === "product");
  const logoLayer    = layers.layers.find((l) => l.type === "logo");
  const textLayers   = layers.layers.filter((l) => l.type === "text" && l.text && l.text.length > 1);
  const accentLayers = layers.layers.filter((l) => l.type === "accent");

  // ── Background animation ───────────────────────────────────────────────────
  const bgAnimStyle = bgLayer && hasAnimations(motionPlan, bgLayer.id)
    ? getLayerStyle(motionPlan, bgLayer.id, frame)
    : null;

  // Fallback Ken Burns when no motion plan exists for background
  const kbProgress = interpolate(framesIntoScene, [0, Math.max(1, sceneEnd - sceneStart)], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  // Bias Ken Burns direction based on focalPoint text
  const focalPoint = analysis?.composition?.focalPoint?.toLowerCase() ?? "center";
  const kbDirY = focalPoint.includes("top")    ?  1
               : focalPoint.includes("bottom") ? -1
               : sceneIndex % 2 === 0          ?  1 : -1;
  const kbDirX = focalPoint.includes("left")   ?  1
               : focalPoint.includes("right")  ? -1
               : 0;

  const kbScale = interpolate(kbProgress, [0, 1], [1.0, 1.08]);
  const kbY     = interpolate(kbProgress, [0, 1], [0, kbDirY * 18]);
  const kbX     = interpolate(kbProgress, [0, 1], [0, kbDirX * 10]);
  const fallbackBgTransform = `scale(${kbScale}) translate(${kbX}px, ${kbY}px)`;

  const bgTransform = bgAnimStyle?.transform ?? fallbackBgTransform;
  const bgOpacity   = (bgAnimStyle?.opacity as number | undefined) ?? 0.85;

  // ── Text reveal spring (per scene) ────────────────────────────────────────
  const textReveal = spring({
    frame: framesIntoScene,
    fps,
    config: { damping: 20, stiffness: 80 },
  });

  // ── Progress bar ──────────────────────────────────────────────────────────
  const progressPct = (frame / totalFrames) * 100;

  // ── Headline & narration words ─────────────────────────────────────────────
  const headlineText  = scene.onScreenText ?? storyboard.title;
  const headlineWords = headlineText.split(" ").filter(Boolean);
  const narrationWords = scene.narration.split(" ").filter(Boolean).slice(0, 22);

  // ─────────────────────────────────────────────────────────────────────────
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0f",
        overflow: "hidden",
        fontFamily: "Inter, system-ui, sans-serif",
      }}
    >
      {/* ── LAYER 1: Background plate ─────────────────────────────────────── */}
      <AbsoluteFill
        style={{
          transform: bgTransform,
          opacity: bgOpacity,
          willChange: "transform",
        }}
      >
        <Img src={safeImageUrl} style={{ width, height, objectFit: "cover" }} />
      </AbsoluteFill>

      {/* ── LAYER 2: Product layer (isolated, independently animated) ─────── */}
      {productLayer && (() => {
        const px = productLayer.bounds.x * scaleX;
        const py = productLayer.bounds.y * scaleY;
        const pw = productLayer.bounds.width  * scaleX;
        const ph = productLayer.bounds.height * scaleY;

        const productAnimStyle = hasAnimations(motionPlan, productLayer.id)
          ? getLayerStyle(motionPlan, productLayer.id, frame)
          : {
              // Fallback: slide up and scale in
              transform: `translateY(${interpolate(textReveal, [0, 1], [40, 0])}px) scale(${interpolate(textReveal, [0, 1], [0.96, 1.0])})`,
              opacity: textReveal,
            };

        return (
          <div
            style={{
              position: "absolute",
              left: px,
              top: py,
              width: pw,
              height: ph,
              overflow: "hidden",
              borderRadius: 16,
              boxShadow: `0 40px 120px rgba(0,0,0,0.65), 0 0 0 1px rgba(255,255,255,0.08)`,
              willChange: "transform, opacity",
              ...productAnimStyle,
            }}
          >
            {/* Show the product region of the source image */}
            <Img
              src={safeImageUrl}
              style={{
                position: "absolute",
                width,
                height,
                left: -px,
                top:  -py,
                objectFit: "cover",
              }}
            />
            {/* Subtle brand colour glow on product bottom */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: `radial-gradient(ellipse at 50% 110%, ${brandColor}44 0%, transparent 65%)`,
                pointerEvents: "none",
              }}
            />
          </div>
        );
      })()}

      {/* ── LAYER 3: Logo layer ───────────────────────────────────────────── */}
      {logoLayer && (() => {
        const lx = logoLayer.bounds.x * scaleX;
        const ly = logoLayer.bounds.y * scaleY;
        const lw = logoLayer.bounds.width  * scaleX;
        const lh = logoLayer.bounds.height * scaleY;
        const logoAnimStyle = hasAnimations(motionPlan, logoLayer.id)
          ? getLayerStyle(motionPlan, logoLayer.id, frame)
          : { opacity: textReveal };

        return (
          <div
            style={{
              position: "absolute",
              left: lx, top: ly, width: lw, height: lh,
              overflow: "hidden",
              willChange: "transform, opacity",
              ...logoAnimStyle,
            }}
          >
            <Img
              src={safeImageUrl}
              style={{ position: "absolute", width, height, left: -lx, top: -ly, objectFit: "cover" }}
            />
          </div>
        );
      })()}

      {/* ── LAYER 4: OCR text layers (positioned from source image) ──────── */}
      {textLayers.map((tl) => {
        const tx = tl.bounds.x * scaleX;
        const ty = tl.bounds.y * scaleY;
        const tw = tl.bounds.width  * scaleX;
        const th = tl.bounds.height * scaleY;
        const tlStyle = hasAnimations(motionPlan, tl.id)
          ? getLayerStyle(motionPlan, tl.id, frame)
          : { opacity: textReveal };

        return (
          <div
            key={tl.id}
            style={{
              position: "absolute",
              left: tx, top: ty, width: tw, height: th,
              display: "flex",
              alignItems: "center",
              overflow: "hidden",
              willChange: "transform, opacity",
              ...tlStyle,
            }}
          >
            <span
              style={{
                color: "white",
                fontSize: Math.max(12, th * 0.55),
                fontWeight: 700,
                textShadow: "0 2px 12px rgba(0,0,0,0.85)",
                whiteSpace: "nowrap",
              }}
            >
              {tl.text}
            </span>
          </div>
        );
      })}

      {/* ── LAYER 5: Accent layers ────────────────────────────────────────── */}
      {accentLayers.map((al) => {
        const ax = al.bounds.x * scaleX;
        const ay = al.bounds.y * scaleY;
        const aw = al.bounds.width  * scaleX;
        const ah = al.bounds.height * scaleY;
        const alStyle = hasAnimations(motionPlan, al.id)
          ? getLayerStyle(motionPlan, al.id, frame)
          : { opacity: textReveal };

        return (
          <div
            key={al.id}
            style={{
              position: "absolute",
              left: ax, top: ay, width: aw, height: ah,
              overflow: "hidden",
              willChange: "transform, opacity",
              ...alStyle,
            }}
          >
            <Img
              src={safeImageUrl}
              style={{ position: "absolute", width, height, left: -ax, top: -ay, objectFit: "cover" }}
            />
          </div>
        );
      })}

      {/* ── Atmospheric gradient overlay (bottom darkening for text) ─────── */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(
            180deg,
            rgba(10,10,15,0.18) 0%,
            rgba(10,10,15,0.00) 30%,
            rgba(10,10,15,0.55) 60%,
            rgba(10,10,15,0.93) 100%
          )`,
          pointerEvents: "none",
        }}
      />

      {/* ── Top vignette ─────────────────────────────────────────────────── */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(
            0deg,
            transparent 0%,
            rgba(10,10,15,0.35) 100%
          )`,
          pointerEvents: "none",
        }}
      />

      {/* ── Scene transition black overlay (fade-through-black) ──────────── */}
      <AbsoluteFill
        style={{
          backgroundColor: "#0a0a0f",
          opacity: overlayOpacity,
          pointerEvents: "none",
        }}
      />

      {/* ── Brand accent line (animated width reveal) ─────────────────────── */}
      <div
        style={{
          position: "absolute",
          left: width * 0.07,
          top: height * 0.055,
          width: interpolate(textReveal, [0, 1], [0, width * 0.14]),
          height: 3,
          backgroundColor: brandColor,
          borderRadius: 3,
          opacity: sceneOpacity,
        }}
      />

      {/* ── Scene index dots ─────────────────────────────────────────────── */}
      <div
        style={{
          position: "absolute",
          left: width * 0.07,
          top: height * 0.055 + 14,
          display: "flex",
          gap: 6,
          opacity: sceneOpacity,
        }}
      >
        {storyboard.scenes.map((_, i) => (
          <div
            key={i}
            style={{
              width: i === sceneIndex ? 20 : 6,
              height: 6,
              borderRadius: 3,
              backgroundColor: i === sceneIndex ? brandColor : "rgba(255,255,255,0.3)",
              transition: "width 0.3s ease",
            }}
          />
        ))}
      </div>

      {/* ── Main scene text block ─────────────────────────────────────────── */}
      <div
        style={{
          position: "absolute",
          left: width * 0.07,
          right: width * 0.07,
          bottom: height * 0.075,
          opacity: sceneOpacity,
        }}
      >
        {/* Scene name label */}
        <div
          style={{
            fontSize: Math.max(18, width * 0.020),
            letterSpacing: 4,
            textTransform: "uppercase",
            color: brandColor,
            fontWeight: 700,
            marginBottom: 14,
            transform: `translateY(${interpolate(textReveal, [0, 1], [20, 0])}px)`,
            opacity: textReveal,
          }}
        >
          {scene.name}
        </div>

        {/* Headline — per-word kinetic stagger */}
        <div
          style={{
            fontSize: Math.max(48, width * 0.074),
            lineHeight: 0.95,
            fontWeight: 800,
            letterSpacing: -2.5,
            color: "white",
            marginBottom: 22,
            display: "flex",
            flexWrap: "wrap",
            columnGap: "0.22em",
            rowGap: "0.08em",
          }}
        >
          {headlineWords.map((word, i) => {
            const wordReveal = spring({
              frame: framesIntoScene - i * 5,
              fps,
              config: { damping: 17, stiffness: 95 },
            });
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  transform: `translateY(${interpolate(wordReveal, [0, 1], [36, 0])}px)`,
                  opacity: wordReveal,
                  willChange: "transform, opacity",
                  // Accent first word with brand color
                  color: i === 0 ? accentColor : "white",
                }}
              >
                {word}
              </span>
            );
          })}
        </div>

        {/* Narration — per-word stagger with softer timing */}
        <div
          style={{
            fontSize: Math.max(20, width * 0.026),
            lineHeight: 1.45,
            display: "flex",
            flexWrap: "wrap",
            columnGap: "0.28em",
            rowGap: "0.05em",
            maxWidth: width * 0.82,
          }}
        >
          {narrationWords.map((word, i) => {
            const delay = headlineWords.length * 5 + i * 3 + 8;
            const wordReveal = spring({
              frame: framesIntoScene - delay,
              fps,
              config: { damping: 22, stiffness: 65 },
            });
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  transform: `translateY(${interpolate(wordReveal, [0, 1], [18, 0])}px)`,
                  opacity: interpolate(wordReveal, [0, 1], [0, 0.72]),
                  color: "rgba(255,255,255,0.72)",
                  willChange: "transform, opacity",
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </div>

      {/* ── Video progress bar ────────────────────────────────────────────── */}
      <div
        style={{
          position: "absolute",
          bottom: height * 0.038,
          left: width * 0.07,
          right: width * 0.07,
          height: 2,
          backgroundColor: "rgba(255,255,255,0.12)",
          borderRadius: 2,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progressPct}%`,
            background: `linear-gradient(90deg, ${brandColor}, ${accentColor})`,
            borderRadius: 2,
          }}
        />
      </div>

      {/* ── MotionForge badge (top right) ─────────────────────────────────── */}
      <div
        style={{
          position: "absolute",
          right: width * 0.06,
          top: height * 0.05,
          border: "1.5px solid rgba(255,255,255,0.22)",
          borderRadius: 999,
          padding: "11px 20px",
          color: "white",
          fontSize: Math.max(16, width * 0.018),
          fontWeight: 500,
          opacity: interpolate(framesIntoScene, [0, 20], [0, 1], {
            extrapolateLeft: "clamp", extrapolateRight: "clamp",
          }),
          backdropFilter: "blur(12px)",
          backgroundColor: "rgba(255,255,255,0.06)",
        }}
      >
        MotionForge
      </div>
    </AbsoluteFill>
  );
}
