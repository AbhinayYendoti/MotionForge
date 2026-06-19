import { getServerEnv } from "./server-env";

const buckets = new Map<string, { count: number; resetAt: number }>();

export function assertRateLimit(key: string) {
  const env = getServerEnv();
  const now = Date.now();
  const current = buckets.get(key);

  if (!current || current.resetAt < now) {
    buckets.set(key, { count: 1, resetAt: now + env.RATE_LIMIT_WINDOW_MS });
    return;
  }

  if (current.count >= env.RATE_LIMIT_MAX) {
    const seconds = Math.ceil((current.resetAt - now) / 1000);
    throw new Error(`Rate limit exceeded. Try again in ${seconds}s.`);
  }

  current.count += 1;
}
