import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main className="mx-auto max-w-page px-6 py-32">
      <Skeleton className="h-10 w-56" />
      <Skeleton className="mt-8 h-40 w-full rounded-hero" />
      <Skeleton className="mt-4 h-40 w-full rounded-hero" />
    </main>
  );
}
