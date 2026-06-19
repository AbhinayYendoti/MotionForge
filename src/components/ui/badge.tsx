import { cn } from "@/lib/utils";

export function Badge({ children, className }: { children: React.ReactNode; className?: string }) {
  return <span className={cn("eyebrow rounded-pill border border-border bg-card px-4 py-2 text-muted-foreground", className)}>{children}</span>;
}
