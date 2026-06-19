import type { Config } from "tailwindcss";
import { withUt } from "uploadthing/tw";

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        background: "rgb(var(--background) / <alpha-value>)",
        foreground: "rgb(var(--foreground) / <alpha-value>)",
        card: "rgb(var(--card) / <alpha-value>)",
        "card-foreground": "rgb(var(--card-foreground) / <alpha-value>)",
        muted: "rgb(var(--muted) / <alpha-value>)",
        "muted-foreground": "rgb(var(--muted-foreground) / <alpha-value>)",
        border: "rgb(var(--border) / <alpha-value>)",
        primary: "rgb(var(--primary) / <alpha-value>)",
        "primary-foreground": "rgb(var(--primary-foreground) / <alpha-value>)",
        secondary: "rgb(var(--secondary) / <alpha-value>)",
        "secondary-foreground": "rgb(var(--secondary-foreground) / <alpha-value>)",
        accent: "rgb(var(--accent) / <alpha-value>)",
        "accent-foreground": "rgb(var(--accent-foreground) / <alpha-value>)",
        destructive: "rgb(var(--destructive) / <alpha-value>)",
        nav: "rgb(var(--nav) / <alpha-value>)",
        footer: "rgb(var(--footer) / <alpha-value>)",
        "footer-foreground": "rgb(var(--footer-foreground) / <alpha-value>)",
        canvas: "rgb(var(--background) / <alpha-value>)",
        ink: "rgb(var(--foreground) / <alpha-value>)",
        charcoal: "rgb(var(--muted-foreground) / <alpha-value>)",
        slate: "rgb(var(--muted-foreground) / <alpha-value>)",
        granite: "rgb(var(--muted-foreground) / <alpha-value>)",
        graphite: "rgb(var(--muted-foreground) / <alpha-value>)",
        dust: "rgb(var(--muted) / <alpha-value>)",
        "inverse-ink": "rgb(var(--primary-foreground) / <alpha-value>)",
        "inverse-canvas": "rgb(var(--footer) / <alpha-value>)",
        "surface-soft": "rgb(var(--secondary) / <alpha-value>)",
        bone: "rgb(var(--muted) / <alpha-value>)",
        hairline: "rgb(var(--border) / <alpha-value>)",
        "hairline-soft": "rgb(var(--border) / <alpha-value>)",
        "signal-orange": "rgb(var(--accent) / <alpha-value>)",
        "light-signal": "rgb(var(--accent) / <alpha-value>)",
        clay: "rgb(var(--accent) / <alpha-value>)",
        "link-blue": "rgb(var(--link) / <alpha-value>)",
        "ghost-cream": "rgb(var(--muted) / <alpha-value>)",
        "mc-red": "#EB001B",
        "mc-yellow": "#F79E1B",
        "block-lime": "rgb(var(--secondary) / <alpha-value>)",
        "block-lilac": "rgb(var(--muted) / <alpha-value>)",
        "block-cream": "rgb(var(--secondary) / <alpha-value>)",
        "block-mint": "rgb(var(--muted) / <alpha-value>)",
        "block-pink": "rgb(var(--muted) / <alpha-value>)",
        "block-coral": "rgb(var(--accent) / <alpha-value>)",
        "block-navy": "rgb(var(--primary) / <alpha-value>)",
        "accent-magenta": "rgb(var(--accent) / <alpha-value>)",
        "semantic-success": "rgb(var(--success) / <alpha-value>)"
      },
      borderRadius: {
        xs: "3px",
        sm: "6px",
        md: "20px",
        lg: "40px",
        xl: "56px",
        pill: "999px",
        hero: "40px",
        nav: "1000px"
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Sofia Sans", "Arial", "sans-serif"],
        mono: ["var(--font-sans)", "Sofia Sans", "Arial", "sans-serif"]
      },
      maxWidth: {
        page: "1280px"
      },
      boxShadow: {
        nav: "var(--shadow-nav)",
        soft: "var(--shadow-soft)",
        deep: "var(--shadow-deep)"
      },
      keyframes: {
        marquee: {
          from: { transform: "translateX(0)" },
          to: { transform: "translateX(-50%)" }
        }
      },
      animation: {
        marquee: "marquee 28s linear infinite"
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
};

export default withUt(config);
