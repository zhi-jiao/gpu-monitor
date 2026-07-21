import { useState } from "react";
import { ServerResult } from "../types";
import { StatusBadge } from "./StatusBadge";
import { GpuBar } from "./GpuBar";
import { DiskRow } from "./DiskRow";
import { MetricRow } from "./MetricRow";
import { Warning } from "@phosphor-icons/react";

interface ServerCardProps {
  server: ServerResult;
  index: number;
}

function bytesToHuman(mb: number): string {
  if (mb >= 1024) return `${(mb / 1024).toFixed(1)}G`;
  return `${mb}M`;
}

export function ServerCard({ server, index }: ServerCardProps) {
  const [expandedGpu, setExpandedGpu] = useState<number | null>(null);
  const isOffline = server.error !== null || server.stats === null;
  const hasWarning =
    !isOffline &&
    server.stats!.disks.some((d) => d.percent >= 90);

  let status: "online" | "offline" | "warning" = "online";
  if (isOffline) status = "offline";
  else if (hasWarning) status = "warning";

  const toggleGpu = (gpuIndex: number) => {
    setExpandedGpu(expandedGpu === gpuIndex ? null : gpuIndex);
  };

  return (
    <article
      className="group rounded-xl border border-[var(--border-default)] bg-[var(--surface-card)] p-4 transition-colors hover:bg-[var(--surface-card-hover)]"
      style={{ animationDelay: `${index * 60}ms` }}
      aria-label={`服务器 ${server.name}，状态${status === "online" ? "在线" : status === "warning" ? "警告" : "离线"}`}
    >
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h2 className="text-base font-semibold text-[var(--text-primary)]">
            {server.name}
          </h2>
          <p className="text-xs text-[var(--text-muted)]">{server.host}</p>
        </div>
        <StatusBadge status={status} />
      </div>

      {isOffline ? (
        <div className="flex items-center gap-2 rounded-lg border border-[var(--status-error)]/20 bg-[var(--status-error)]/10 px-3 py-4 text-sm text-[var(--status-error)]">
          <Warning size={18} aria-hidden="true" />
          <span>{server.error || "无法获取数据"}</span>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <MetricRow label="CPU" value={server.stats!.cpu.toFixed(1)} unit="%" />
            <MetricRow label="内存" value={server.stats!.mem.toFixed(1)} unit="%" />
          </div>

          {server.stats!.gpus.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs font-medium uppercase tracking-wider text-[var(--text-tertiary)]">
                GPU
              </span>
              <div className="space-y-2">
                {server.stats!.gpus.map((gpu) => {
                  const isExpanded = expandedGpu === gpu.index;
                  const hasProcesses = gpu.processes.length > 0;
                  return (
                    <div
                      key={gpu.index}
                      className="rounded-lg border border-[var(--border-subtle)] p-2.5"
                    >
                      <button
                        type="button"
                        className="w-full cursor-pointer text-left"
                        onClick={() => toggleGpu(gpu.index)}
                        aria-expanded={isExpanded}
                      >
                        <GpuBar
                          index={gpu.index}
                          model={gpu.model}
                          util={gpu.util}
                          memUsed={gpu.mem_used}
                          memTotal={gpu.mem_total}
                          memPercent={gpu.mem_percent}
                          temp={gpu.temp}
                        />
                      </button>

                      {isExpanded && hasProcesses && (
                        <div className="mt-2 space-y-1.5 border-t border-[var(--border-subtle)] pt-2">
                          <span className="text-xs font-medium text-[var(--text-tertiary)]">
                            进程详情
                          </span>
                          {gpu.processes.map((proc, i) => (
                            <div
                              key={i}
                              className="flex items-center justify-between text-xs"
                            >
                              <span className="text-[var(--text-secondary)]">
                                {proc.user}
                                <span className="ml-2 text-[var(--text-muted)]">{proc.name}</span>
                              </span>
                              <span className="font-mono text-[var(--text-primary)]">
                                {bytesToHuman(proc.mem_mb)}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}

                      {isExpanded && !hasProcesses && (
                        <div className="mt-2 border-t border-[var(--border-subtle)] pt-2 text-xs text-[var(--text-muted)]">
                          无活动进程
                        </div>
                      )}

                      {hasProcesses && !isExpanded && (
                        <div className="mt-1 text-xs text-[var(--text-tertiary)]">
                          {gpu.processes.length} 个进程
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {server.stats!.disks.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs font-medium uppercase tracking-wider text-[var(--text-tertiary)]">
                磁盘
              </span>
              <div className="space-y-2">
                {server.stats!.disks.map((disk) => (
                  <DiskRow
                    key={disk.mount}
                    mount={disk.mount}
                    total={disk.total}
                    percent={disk.percent}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </article>
  );
}