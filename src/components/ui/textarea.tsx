import * as React from "react";
import { cn } from "@/lib/utils";

export type TextareaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>;

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(({ className, ...props }, ref) => {
  return (
    <textarea
      ref={ref}
      className={cn(
        "focus-ring min-h-32 w-full rounded-[24px] border border-border bg-card px-6 py-4 text-[16px] font-[450] leading-[1.4] text-foreground placeholder:text-muted-foreground",
        className
      )}
      {...props}
    />
  );
});
Textarea.displayName = "Textarea";

export { Textarea };
