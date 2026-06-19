import { z } from "zod";

// ── Environment schema ─────────────────────────────────────────────────────────
// All variables validated at call-time, not at import-time, so Next.js build
// does not fail when running in environments that only have a subset of vars
// (e.g. CI preview builds without UploadThing secrets).

const envSchema = z.object({
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: z.string().min(1, "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY is required"),
  CLERK_SECRET_KEY: z.string().min(1, "CLERK_SECRET_KEY is required"),

  // UploadThing — v7 uses UPLOADTHING_TOKEN as the unified credential.
  // UPLOADTHING_SECRET and UPLOADTHING_APP_ID are kept for compatibility.
  UPLOADTHING_TOKEN: z.string().min(1, "UPLOADTHING_TOKEN is required").optional(),
  UPLOADTHING_SECRET: z.string().min(1).optional(),
  UPLOADTHING_APP_ID: z.string().min(1).optional(),

  // Backend API URL — required so we never silently hit localhost in production.
  BACKEND_URL: z.string().url("BACKEND_URL must be a valid URL (e.g. https://your-api.onrender.com)").optional(),
  NEXT_PUBLIC_BACKEND_URL: z.string().url("NEXT_PUBLIC_BACKEND_URL must be a valid URL").optional(),

  APP_URL: z.string().url().default("http://localhost:3000"),

  RATE_LIMIT_WINDOW_MS: z.coerce.number().int().positive().default(60_000),
  RATE_LIMIT_MAX: z.coerce.number().int().positive().default(30),
}).refine(
  (data) => !!(data.UPLOADTHING_TOKEN || data.UPLOADTHING_SECRET),
  { message: "Either UPLOADTHING_TOKEN or UPLOADTHING_SECRET must be set" }
).refine(
  (data) => !!(data.BACKEND_URL || data.NEXT_PUBLIC_BACKEND_URL),
  { message: "Either BACKEND_URL or NEXT_PUBLIC_BACKEND_URL must be set" }
);

export type ServerEnv = z.infer<typeof envSchema>;

export function getServerEnv(): ServerEnv {
  const result = envSchema.safeParse(process.env);
  if (!result.success) {
    const details = result.error.issues
      .map((issue) => `  • ${issue.path.join(".") || "env"}: ${issue.message}`)
      .join("\n");
    throw new Error(
      `MotionForge environment is misconfigured:\n${details}\n\n` +
      "Check your .env file or Vercel/Render environment settings."
    );
  }
  return result.data;
}
