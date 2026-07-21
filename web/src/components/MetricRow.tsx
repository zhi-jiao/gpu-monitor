interface MetricRowProps {
  label: string;
  value: string | number;
  unit?: string;
  emphasis?: boolean;
}

export function MetricRow({ label, value, unit, emphasis }: MetricRowProps) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-[var(--text-tertiary)]">{label}</span>
      <span
        className={`font-mono text-sm ${emphasis ? "font-medium text-[var(--text-primary)]" : "text-[var(--text-secondary)]"}`}
      >
        {value}
        {unit ? <span className="ml-0.5 text-[var(--text-muted)]">{unit}</span> : null}
      </span>
    </div>
  );
}
