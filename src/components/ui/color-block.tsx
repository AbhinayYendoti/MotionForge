import { cn } from "@/lib/utils";

const variants = {
  lime: "bg-secondary text-secondary-foreground",
  lilac: "bg-muted text-foreground",
  cream: "bg-secondary text-secondary-foreground",
  mint: "bg-muted text-foreground",
  pink: "bg-muted text-foreground",
  coral: "bg-accent text-accent-foreground",
  navy: "bg-footer text-footer-foreground"
};

export function ColorBlock({
  variant = "lime",
  className,
  children
}: {
  variant?: keyof typeof variants;
  className?: string;
  children: React.ReactNode;
}) {
  return <section className={cn("rounded-hero p-8 shadow-soft md:p-12", variants[variant], className)}>{children}</section>;
}
