import { ArrowClockwise, Cpu } from "@phosphor-icons/react";

interface PageHeaderProps {
  title: string;
  lastUpdated: Date | null;
  loading: boolean;
  onRefresh: () => void;
}

export function PageHeader({ title, lastUpdated, loading, onRefresh }: PageHeaderProps) {
  const formattedTime = lastUpdated
    ? lastUpdated.toLocaleTimeString("zh-CN", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "--:--:--";

  return (
    <header className="sticky top-0 z-10 border-b border-[var(--border-subtle)] bg-[var(--surface-panel)]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1400px] items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--accent-primary)]/20 text-[var(--accent-bright)]">
            <Cpu size={20} weight="fill" />
          </div>
          <h1 className="text-lg font-semibold tracking-tight">{title}</h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="hidden text-sm text-[var(--text-tertiary)] sm:inline">
            更新于 {formattedTime}
          </span>
          <button
            type="button"
            onClick={onRefresh}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-md border border-[var(--border-default)] bg-[rgba(255,255,255,0.03)] px-3 py-1.5 text-sm text-[var(--text-secondary)] transition-colors hover:bg-[rgba(255,255,255,0.05)] disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="刷新数据"
          >
            <ArrowClockwise
              size={16}
              className={loading ? "animate-spin" : ""}
              aria-hidden="true"
            />
            <span className="hidden sm:inline">刷新</span>
          </button>
        </div>
      </div>
    </header>
  );
}
