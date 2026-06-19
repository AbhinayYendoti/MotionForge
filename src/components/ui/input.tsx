import * as React from "react";
import { cn } from "@/lib/utils";

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, ...props }, ref) => {
  return (
    <input
      ref={ref}
      className={cn(
        "focus-ring min-h-12 w-full rounded-pill border border-border bg-card px-6 py-3 text-[16px] font-[450] leading-[1.4] text-foreground placeholder:text-muted-foreground",
        className
      )}
      {...props}
    />
  );
});
Input.displayName = "Input";

export { Input };
