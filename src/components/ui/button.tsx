import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "focus-ring inline-flex min-h-11 items-center justify-center rounded-md border-[1.5px] px-6 py-1.5 text-[16px] font-[500] leading-[1.3] tracking-[-0.02em] transition-transform duration-150 active:translate-y-px active:scale-[0.98] disabled:pointer-events-none disabled:opacity-60",
  {
    variants: {
      variant: {
        primary: "border-primary bg-primary text-primary-foreground",
        secondary: "border-primary bg-card text-foreground",
        outline: "border-primary bg-card text-foreground",
        magenta: "border-accent bg-accent text-accent-foreground",
        ghost: "border-transparent bg-transparent text-foreground hover:bg-card/70"
      },
      size: {
        default: "px-6 py-1.5",
        sm: "min-h-10 px-5 py-1 text-[15px]",
        lg: "min-h-12 px-8 py-2 text-[16px]",
        icon: "h-12 w-12 rounded-full p-0"
      }
    },
    defaultVariants: {
      variant: "primary",
      size: "default"
    }
  }
);

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, size, ...props }, ref) => {
  return <button className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
});
Button.displayName = "Button";

export { Button, buttonVariants };
