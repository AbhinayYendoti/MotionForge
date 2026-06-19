import Link, { type LinkProps } from "next/link";
import { type AnchorHTMLAttributes } from "react";
import { buttonVariants, type ButtonProps } from "./button";
import { cn } from "@/lib/utils";

type LinkButtonProps = LinkProps &
  AnchorHTMLAttributes<HTMLAnchorElement> & {
    variant?: ButtonProps["variant"];
    size?: ButtonProps["size"];
  };

export function LinkButton({ className, variant, size, ...props }: LinkButtonProps) {
  return <Link className={cn(buttonVariants({ variant, size, className }))} {...props} />;
}
