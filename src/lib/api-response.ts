import { NextResponse } from "next/server";
import { ZodError } from "zod";
import { logger } from "./logger";

export function jsonOk<T>(data: T, init?: ResponseInit) {
  return NextResponse.json({ ok: true, data }, init);
}

export function jsonError(error: unknown, status = 500) {
  if (error instanceof ZodError) {
    return NextResponse.json({ ok: false, error: "Validation failed", issues: error.flatten() }, { status: 422 });
  }

  const message = error instanceof Error ? error.message : "Unexpected server error";
  logger.error(message, { status });
  return NextResponse.json({ ok: false, error: message }, { status });
}
