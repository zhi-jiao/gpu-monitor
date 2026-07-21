#!/usr/bin/env python3
"""Self-contained collector that prints local GPU/server stats as JSON.

Run locally for testing, or pipe to a remote host via SSH:
    ssh user@gpu-server python3 - < agent/collector.py
"""

from __future__ import annotations

import json
import os
import pwd
import subprocess
import sys
from typing import TypedDict

import psutil

DEFAULT_MOUNTS = ("/mnt/data", "/", "/home")


class GpuProcessDict(TypedDict):
    user: str
    name: str
    mem_mb: int


class GpuInfoDict(TypedDict):
    index: int
    model: str
    util: int
    mem_used: int
    mem_total: int
    mem_percent: float
    temp: int
    processes: list[GpuProcessDict]


class DiskInfoDict(TypedDict):
    mount: str
    total: str
    percent: float


class ServerStatsDict(TypedDict):
    cpu: float
    mem: float
    gpus: list[GpuInfoDict]
    disks: list[DiskInfoDict]


def bytes_to_human(n: float) -> str:
    units = ("B", "K", "M", "G", "T", "P")
    for unit in units:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}E"


def _resolve_user(pid: int) -> str:
    try:
        uid = os.stat(f"/proc/{pid}").st_uid
    except (FileNotFoundError, OSError):
        return "unknown"
    try:
        return pwd.getpwuid(uid).pw_name
    except KeyError:
        return "unknown"


def _parse_gpu_line(line: str) -> GpuInfoDict:
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 6:
        raise ValueError(f"unexpected nvidia-smi line: {line!r}")
    index, model, util, mem_used, mem_total, temp = parts
    used = int(mem_used)
    total = int(mem_total)
    mem_percent = round(used / total * 100, 1) if total > 0 else 0.0
    return {
        "index": int(index),
        "model": model,
        "util": int(util),
        "mem_used": used,
        "mem_total": total,
        "mem_percent": mem_percent,
        "temp": int(temp),
        "processes": [],
    }


def get_gpus() -> list[GpuInfoDict]:
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        return []

    return [
        _parse_gpu_line(line)
        for line in output.strip().splitlines()
        if line.strip()
    ]


def _build_bus_id_map() -> dict[str, int]:
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,pci.bus_id", "--format=csv,noheader"],
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        return {}
    mapping: dict[str, int] = {}
    for line in output.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 2 and parts[0].isdigit():
            mapping[parts[1]] = int(parts[0])
    return mapping


def get_gpu_processes() -> list[dict]:
    """Return list of {gpu_index, user, name, mem_mb} for all GPU processes."""
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-compute-apps=gpu_bus_id,pid,process_name,used_gpu_memory",
                "--format=csv,noheader,nounits",
            ],
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        return []

    bus_to_gpu = _build_bus_id_map()
    processes: list[dict] = []
    for line in output.strip().splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            continue
        bus_id, pid_str, pname, mem_str = parts
        try:
            pid = int(pid_str)
            mem_mb = int(mem_str)
        except ValueError:
            continue
        gpu_index = bus_to_gpu.get(bus_id)
        if gpu_index is None:
            continue
        processes.append(
            {
                "gpu_index": gpu_index,
                "user": _resolve_user(pid),
                "name": pname,
                "mem_mb": mem_mb,
            }
        )
    return processes


def _get_disk(mount: str) -> DiskInfoDict | None:
    try:
        usage = psutil.disk_usage(mount)
    except OSError:
        return None
    return {
        "mount": mount,
        "total": bytes_to_human(usage.total),
        "percent": usage.percent,
    }


def get_disks(mounts: tuple[str, ...] = DEFAULT_MOUNTS) -> list[DiskInfoDict]:
    available = {
        partition.mountpoint for partition in psutil.disk_partitions(all=False)
    }
    return [
        disk
        for mount in mounts
        if mount in available and (disk := _get_disk(mount)) is not None
    ]


def collect() -> ServerStatsDict:
    gpus = get_gpus()
    processes = get_gpu_processes()
    for proc in processes:
        idx = proc["gpu_index"]
        for gpu in gpus:
            if gpu["index"] == idx:
                gpu["processes"].append(
                    {"user": proc["user"], "name": proc["name"], "mem_mb": proc["mem_mb"]}
                )
                break
    return {
        "cpu": psutil.cpu_percent(interval=0.1),
        "mem": psutil.virtual_memory().percent,
        "gpus": gpus,
        "disks": get_disks(),
    }


if __name__ == "__main__":
    print(json.dumps(collect()))
    sys.stdout.flush()