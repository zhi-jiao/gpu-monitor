import { useEffect, useState } from "react";
import { ServerResult } from "./types";
import { PageHeader } from "./components/PageHeader";
import { ServerCard } from "./components/ServerCard";
import { SkeletonCard } from "./components/SkeletonCard";

const POLL_INTERVAL = 5000;

function App() {
  const [servers, setServers] = useState<ServerResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/stats");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data: ServerResult[] = await response.json();
      setServers(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch");
    } finally {
      setLoading(false);
      setInitialLoad(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-[100dvb] bg-[var(--surface-page)] text-[var(--text-primary)]">
      <PageHeader
        title="GPU Monitor"
        lastUpdated={lastUpdated}
        loading={loading}
        onRefresh={fetchData}
      />
      <main className="mx-auto max-w-[1400px] px-4 py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-6 rounded-lg border border-[var(--status-error)]/30 bg-[var(--status-error)]/10 px-4 py-3 text-sm text-[var(--status-error)]">
            数据加载失败: {error}
          </div>
        )}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {initialLoad ? (
            <SkeletonCard />
          ) : (
            servers.map((server, index) => (
              <ServerCard key={server.name} server={server} index={index} />
            ))
          )}
        </div>
        {!initialLoad && servers.length === 0 && !loading && !error && (
          <div className="py-20 text-center text-[var(--text-tertiary)]">
            暂无服务器数据
          </div>
        )}
      </main>
    </div>
  );
}

export default App;