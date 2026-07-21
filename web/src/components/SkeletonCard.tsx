export function SkeletonCard() {
  return (
    <div className="rounded-xl border border-[var(--border-default)] bg-[var(--surface-card)] p-4 animate-pulse">
      <div className="mb-4 flex items-start justify-between">
        <div className="space-y-2">
          <div className="h-4 w-24 rounded bg-[var(--surface-elevated)]" />
          <div className="h-3 w-16 rounded bg-[var(--surface-elevated)]" />
        </div>
        <div className="h-5 w-14 rounded-full bg-[var(--surface-elevated)]" />
      </div>
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="h-10 rounded bg-[var(--surface-elevated)]" />
          <div className="h-10 rounded bg-[var(--surface-elevated)]" />
        </div>
        <div className="space-y-2">
          <div className="h-3 w-8 rounded bg-[var(--surface-elevated)]" />
          <div className="space-y-3">
            <div className="h-10 rounded bg-[var(--surface-elevated)]" />
            <div className="h-10 rounded bg-[var(--surface-elevated)]" />
          </div>
        </div>
      </div>
    </div>
  );
}