import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";
import { Menu, Search } from "lucide-react";
import Link from "next/link";
import { LinkButton } from "@/components/ui/link-button";
import { Button } from "@/components/ui/button";
import { isClerkConfigured } from "@/lib/clerk-config";
import { ThemeToggle } from "@/components/theme/theme-toggle";

export function SiteNav() {
  const clerkConfigured = isClerkConfigured();

  return (
    <header className="pointer-events-none fixed left-0 right-0 top-6 z-40 px-4">
      <nav className="pointer-events-auto mx-auto flex max-w-page items-center justify-between rounded-nav bg-nav/95 px-5 py-3 text-foreground shadow-nav backdrop-blur md:px-10">
        <Link href="/" className="flex items-center gap-3 text-[18px] font-[700] tracking-[-0.02em]">
          <span className="relative flex h-9 w-12 items-center">
            <span className="absolute left-0 h-8 w-8 rounded-full bg-mc-red" />
            <span className="absolute left-5 h-8 w-8 rounded-full bg-mc-yellow mix-blend-multiply" />
          </span>
          <span className="hidden sm:inline">MotionForge</span>
        </Link>
        <div className="hidden items-center gap-10 text-[16px] font-[500] leading-none tracking-[-0.03em] lg:flex">
          <Link href="/#pipeline">Pipeline</Link>
          <Link href="/#rendering">Rendering</Link>
          <Link href="/#quality">Quality</Link>
          <Link href="/dashboard">Dashboard</Link>
        </div>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Button variant="ghost" size="icon" className="hidden border-border bg-card md:inline-flex" aria-label="Search">
            <Search size={18} />
          </Button>
          {clerkConfigured ? (
            <>
              <SignedOut>
                <SignInButton mode="modal">
                  <Button variant="secondary" size="sm" className="hidden sm:inline-flex">
                    Sign in
                  </Button>
                </SignInButton>
                <LinkButton href="/dashboard" size="sm" className="hidden sm:inline-flex">
                  Get started
                </LinkButton>
              </SignedOut>
              <SignedIn>
                <LinkButton href="/dashboard" variant="secondary" size="sm" className="hidden sm:inline-flex">
                  Dashboard
                </LinkButton>
                <UserButton />
              </SignedIn>
            </>
          ) : (
            <LinkButton href="/dashboard" size="sm" className="hidden sm:inline-flex">
              Get started
            </LinkButton>
          )}
          <Button variant="ghost" size="icon" className="md:hidden" aria-label="Open menu">
            <Menu size={20} />
          </Button>
        </div>
      </nav>
    </header>
  );
}
