from __future__ import annotations

import json
import os
from pathlib import Path

import anyio
import paramiko
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, ValidationError

app = FastAPI()

_DEFAULT_SERVERS_PATH = Path(__file__).parent.parent / "servers.json"
_COLLECTOR_SCRIPT = (
    Path(__file__).parent.parent / "agent" / "collector.py"
).read_text(encoding="utf-8")


class GpuProcessInfo(BaseModel):
    """Information about a process running on a GPU."""

    model_config = ConfigDict(frozen=True)

    user: str
    name: str
    mem_mb: int


class GpuInfo(BaseModel):
    """Metrics for a single NVIDIA GPU."""

    model_config = ConfigDict(frozen=True)

    index: int
    model: str
    util: int
    mem_used: int
    mem_total: int
    mem_percent: float
    temp: int
    processes: list[GpuProcessInfo]


class DiskInfo(BaseModel):
    """Metrics for a single disk mount point."""

    model_config = ConfigDict(frozen=True)

    mount: str
    total: str
    percent: float


class ServerStats(BaseModel):
    """Health metrics collected from a remote server."""

    model_config = ConfigDict(frozen=True)

    cpu: float
    mem: float
    gpus: list[GpuInfo]
    disks: list[DiskInfo]


class ServerSshConfig(BaseModel):
    """SSH connection details for one GPU server."""

    model_config = ConfigDict(frozen=True)

    name: str
    host: str
    port: int = 22
    user: str
    key: str


class ServerResult(BaseModel):
    """Result of collecting metrics from one remote server."""

    model_config = ConfigDict(frozen=True)

    name: str
    host: str
    stats: ServerStats | None = None
    error: str | None = None


def load_servers(path: Path | None = None) -> tuple[ServerSshConfig, ...]:
    """Load the SSH server list from env var or a JSON file."""
    env_data = os.environ.get("GPU_MONITOR_SERVERS")
    if env_data:
        data = json.loads(env_data)
    else:
        if path is None:
            path = _DEFAULT_SERVERS_PATH
        data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(
        ServerSshConfig(name=name, **cfg) for name, cfg in data.items()
    )


def _collect_via_ssh(config: ServerSshConfig, script: str) -> ServerStats:
    """SSH to a server, run the collector script, and parse the JSON output."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_path = Path(config.key).expanduser()
    client.connect(
        hostname=config.host,
        port=config.port,
        username=config.user,
        key_filename=str(key_path),
        timeout=10,
        banner_timeout=10,
        auth_timeout=10,
    )
    try:
        stdin, stdout, stderr = client.exec_command("python3 -")
        stdin.write(script)
        stdin.channel.shutdown_write()
        output = stdout.read().decode("utf-8").strip()
        error = stderr.read().decode("utf-8").strip()
        if error:
            raise RuntimeError(error)
        return ServerStats.model_validate(json.loads(output))
    finally:
        client.close()


async def collect_one(config: ServerSshConfig) -> ServerResult:
    """Collect metrics from a single remote server."""
    try:
        stats = await anyio.to_thread.run_sync(
            _collect_via_ssh, config, _COLLECTOR_SCRIPT
        )
    except (OSError, ValueError, ValidationError, paramiko.SSHException) as exc:
        return ServerResult(name=config.name, host=config.host, error=str(exc))
    return ServerResult(name=config.name, host=config.host, stats=stats)


async def collect_all(
    servers: tuple[ServerSshConfig, ...],
) -> list[ServerResult]:
    """Collect metrics from all configured servers concurrently."""
    results: list[ServerResult | None] = [None] * len(servers)
    async with anyio.create_task_group() as tg:

        async def runner(idx: int, server: ServerSshConfig) -> None:
            results[idx] = await collect_one(server)

        for idx, server in enumerate(servers):
            tg.start_soon(runner, idx, server)

    filled: list[ServerResult] = []
    for result in results:
        if result is None:
            raise RuntimeError("unfilled result slot")
        filled.append(result)
    return filled


SERVERS = load_servers()


@app.get("/api/stats")
async def api_stats() -> list[ServerResult]:
    """Return the aggregated metrics as JSON."""
    return await collect_all(SERVERS)


_STATIC_DIST_DIR = Path(__file__).parent.parent / "web" / "dist"
if _STATIC_DIST_DIR.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=str(_STATIC_DIST_DIR), html=True),
        name="static",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)
