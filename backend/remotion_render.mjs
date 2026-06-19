/**
 * remotion_render.mjs — Remotion render subprocess for MotionForge.
 *
 * Called by the Python render worker:
 *   node backend/remotion_render.mjs <path/to/job.json>
 *
 * The entry point is resolved relative to this script's own directory so it
 * works regardless of the process working directory.
 */
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// __dirname equivalent in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

const { bundle }                        = await import('@remotion/bundler');
const { renderMedia, selectComposition } = await import('@remotion/renderer');

const FORMATS = {
  reel:      { width: 1080, height: 1920 },
  landscape: { width: 1920, height: 1080 },
  square:    { width: 1080, height: 1080 },
};

const jobPath = process.argv[2];
if (!jobPath) {
  console.error(JSON.stringify({ level: 'error', message: 'Render job JSON path is required as argv[2].' }));
  process.exit(1);
}

try {
  const job = JSON.parse(await readFile(jobPath, 'utf-8'));

  if (!job.storyboard || !job.motionPlan || !job.layers) {
    throw new Error('Job manifest is missing required fields: storyboard, motionPlan, or layers.');
  }

  const dimensions      = FORMATS[job.format] ?? FORMATS.reel;
  const durationInFrames = Math.max(1, Math.ceil((job.storyboard.totalDurationSeconds ?? 5) * 30));

  // Resolve the Remotion composition entry point relative to the repo root
  // (one directory above this script's location: backend/../src/remotion/index.ts)
  const entryPoint = path.resolve(__dirname, '..', 'src', 'remotion', 'index.ts');

  const inputProps = {
    imageUrl:   job.imageUrl,
    storyboard: job.storyboard,
    motionPlan: job.motionPlan,
    layers:     job.layers,
    analysis:   job.analysis ?? null,
    width:      dimensions.width,
    height:     dimensions.height,
  };

  const serveUrl = await bundle({ entryPoint, webpackOverride: (cfg) => cfg });
  const composition = await selectComposition({ serveUrl, id: 'MotionForgeVideo', inputProps });

  await renderMedia({
    composition: {
      ...composition,
      durationInFrames,
      fps: 30,
      width:  dimensions.width,
      height: dimensions.height,
    },
    serveUrl,
    codec: 'h264',
    outputLocation: job.outputLocation,
    inputProps,
  });

  process.stdout.write(
    `Rendered ${job.format} ${dimensions.width}x${dimensions.height} ` +
    `at 30fps for ${durationInFrames} frames.`
  );
  process.exit(0);

} catch (err) {
  console.error(JSON.stringify({
    level: 'error',
    message: 'Remotion render failed',
    error: err instanceof Error ? err.message : String(err),
    stack: err instanceof Error ? err.stack : undefined,
  }));
  process.exit(1);
}
