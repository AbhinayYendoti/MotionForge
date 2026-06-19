"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

const options = [
  { value: "light", label: "Light theme", icon: Sun },
  { value: "dark", label: "Dark theme", icon: Moon },
  { value: "system", label: "System theme", icon: Monitor }
] as const;

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  return (
    <div
      className="flex h-10 w-[112px] shrink-0 items-center justify-center gap-0.5 rounded-pill border border-border bg-secondary p-1"
      aria-label="Theme preference"
      role="group"
    >
      {options.map(({ value, label, icon: Icon }) => {
        const selected = mounted && theme === value;
        return (
          <button
            key={value}
            type="button"
            title={label}
            aria-label={label}
            aria-pressed={selected}
            onClick={() => setTheme(value)}
            className={cn(
              "focus-ring flex h-8 w-8 items-center justify-center rounded-full text-muted-foreground transition-colors duration-200",
              selected && "bg-card text-foreground shadow-nav"
            )}
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
          </button>
        );
      })}
    </div>
  );
}
