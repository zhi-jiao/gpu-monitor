export interface GpuProcessInfo {
  user: string;
  name: string;
  mem_mb: number;
}

export interface GpuInfo {
  index: number;
  model: string;
  util: number;
  mem_used: number;
  mem_total: number;
  mem_percent: number;
  temp: number;
  processes: GpuProcessInfo[];
}

export interface DiskInfo {
  mount: string;
  total: string;
  percent: number;
}

export interface ServerStats {
  cpu: number;
  mem: number;
  gpus: GpuInfo[];
  disks: DiskInfo[];
}

export interface ServerResult {
  name: string;
  host: string;
  stats: ServerStats | null;
  error: string | null;
}
