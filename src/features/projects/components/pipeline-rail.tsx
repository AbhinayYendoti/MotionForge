import { Check, Loader2, X } from "lucide-react";
import { cn } from "@/lib/utils";

type Step = {
  id: string;
  label: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
};

export function PipelineRail({ steps }: { steps: Step[] }) {
  return (
    <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-9">
      {steps.map((step) => (
        <div key={step.id} className="rounded-[28px] border border-border bg-card p-4 text-card-foreground shadow-nav">
          <div
            className={cn(
              "mb-4 flex h-10 w-10 items-center justify-center rounded-full",
              step.status === "COMPLETED" && "bg-primary text-primary-foreground",
              step.status === "RUNNING" && "bg-accent text-accent-foreground",
              step.status === "FAILED" && "bg-accent text-accent-foreground",
              step.status === "PENDING" && "bg-background text-foreground"
            )}
          >
            {step.status === "COMPLETED" ? <Check size={18} /> : null}
            {step.status === "RUNNING" ? <Loader2 size={18} className="animate-spin" /> : null}
            {step.status === "FAILED" ? <X size={18} /> : null}
          </div>
          <p className="text-[15px] font-[500] leading-tight tracking-[-0.02em]">{step.label}</p>
          <p className="mt-3 text-[12px] font-[700] uppercase tracking-[0.04em] text-muted-foreground">{step.status.toLowerCase()}</p>
        </div>
      ))}
    </div>
  );
}
