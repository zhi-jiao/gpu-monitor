interface StatusBadgeProps {
  status: "online" | "offline" | "warning";
  label?: string;
}

const config = {
  online: {
    dot: "bg-[var(--status-success)]",
    text: "text-[var(--status-success)]",
    label: "在线",
  },
  offline: {
    dot: "bg-[var(--status-error)]",
    text: "text-[var(--status-error)]",
    label: "离线",
  },
  warning: {
    dot: "bg-[var(--status-warning)]",
    text: "text-[var(--status-warning)]",
    label: "警告",
  },
};

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const cfg = config[status];
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${cfg.text}`}>
      <span className={`h-2 w-2 rounded-full ${cfg.dot}`} aria-hidden="true" />
      {label ?? cfg.label}
    </span>
  );
}
