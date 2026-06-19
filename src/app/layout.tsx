import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { Sofia_Sans } from "next/font/google";
import { isClerkConfigured } from "@/lib/clerk-config";
import { ThemeProvider } from "@/components/theme/theme-provider";
import "./globals.css";

const sofia = Sofia_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  weight: ["400", "500", "700"],
  display: "swap"
});

export const metadata: Metadata = {
  title: {
    default: "MotionForge - Turn static creatives into motion campaigns",
    template: "%s | MotionForge"
  },
  description: "MotionForge transforms static marketing creatives into professional motion graphics videos through a structured, explainable generation pipeline.",
  openGraph: {
    title: "MotionForge",
    description: "Turn static creatives into motion campaigns.",
    type: "website"
  },
  metadataBase: new URL(process.env.APP_URL ?? "http://localhost:3000")
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  if (!isClerkConfigured()) {
    return (
      <html lang="en" className={sofia.variable} suppressHydrationWarning>
        <body>
          <ThemeProvider>{children}</ThemeProvider>
        </body>
      </html>
    );
  }

  return (
    <ClerkProvider>
      <html lang="en" className={sofia.variable} suppressHydrationWarning>
        <body>
          <ThemeProvider>{children}</ThemeProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
