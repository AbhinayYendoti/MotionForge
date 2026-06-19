export function JsonPanel({ title, value }: { title: string; value: unknown }) {
  if (!value) return null;

  return (
    <section className="rounded-hero border border-border bg-card p-6 text-card-foreground shadow-nav">
      <p className="eyebrow mb-4">{title}</p>
      <pre className="max-h-[360px] overflow-auto whitespace-pre-wrap rounded-[24px] bg-background p-4 text-[13px] leading-relaxed text-muted-foreground">
        {JSON.stringify(value, null, 2)}
      </pre>
    </section>
  );
}
