export function isClerkConfigured() {
  const key = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  if (!key || key.includes("dummy")) return false;

  const encoded = key.replace(/^pk_(test|live)_/, "");
  try {
    const decoded = Buffer.from(encoded, "base64").toString("utf8");
    return !decoded.includes("clerk.example");
  } catch {
    return true;
  }
}
