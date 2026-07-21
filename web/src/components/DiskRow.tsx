interface DiskRowProps {
  mount: string;
  total: string;
  percent: number;
}

export function DiskRow({ mount, total, percent }: DiskRowProps) {
  const isWarning = percent >= 90;
  const barColor = isWarning
    ? "bg-[var(--status-warning)]"
    : "bg-[var(--accent-bright)]";

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-[var(--text-secondary)]">{mount}</span>
        <span className="font-mono text-[var(--text-primary)]">
          {total} · {percent}%
          {isWarning && <span className="ml-1 text-[var(--status-warning)]">!!!</span>}
        </span>
      </div>
      <div className="h-1 w-full overflow-hidden rounded-full bg-[var(--surface-elevated)]">
        <div
          className={`h-full rounded-full transition-all duration-150 ease-out ${barColor}`}
          style={{ width: `${percent}%` }}
          aria-hidden="true"
        />
      </div>
    </div>
  );
}
