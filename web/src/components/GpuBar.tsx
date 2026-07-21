interface GpuBarProps {
  index: number;
  model: string;
  util: number;
  memUsed: number;
  memTotal: number;
  memPercent: number;
  temp: number;
}

function bytesToHuman(mb: number): string {
  if (mb >= 1024) return `${(mb / 1024).toFixed(1)}G`;
  return `${mb}M`;
}

export function GpuBar({ index, model, util, memUsed, memTotal, memPercent, temp }: GpuBarProps) {
  const isWarning = util >= 90 || memPercent >= 90 || temp >= 85;
  const barColor = isWarning
    ? "bg-[var(--status-warning)]"
    : "bg-[var(--accent-bright)]";

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-[var(--text-primary)]">
          GPU {index} <span className="font-normal text-[var(--text-tertiary)]">{model}</span>
        </span>
        <span title="温度" className={temp >= 85 ? "font-mono text-[var(--status-warning)]" : "font-mono text-[var(--text-primary)]"}>
          {temp}°C
        </span>
      </div>
      <div className="flex items-center justify-between text-xs font-mono">
        <span className="text-[var(--text-secondary)]">
          {bytesToHuman(memUsed)} / {bytesToHuman(memTotal)}
        </span>
        <span className="text-[var(--text-primary)]">{util}%</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-[var(--surface-elevated)]">
        <div
          className={`h-full rounded-full transition-all duration-150 ease-out ${barColor}`}
          style={{ width: `${util}%` }}
          aria-hidden="true"
        />
      </div>
    </div>
  );
}