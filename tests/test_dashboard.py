from __future__ import annotations

from pathlib import Path

import pytest
from app import main
from app.main import GpuInfo, GpuProcessInfo, ServerSshConfig, ServerStats


def test_load_servers_from_file(tmp_path: Path) -> None:
    config_path = tmp_path / "servers.json"
    config_path.write_text(
        '{"server1": {"host": "10.0.0.1", "port": 22, '
        '"user": "u", "key": "~/.ssh/id_rsa"}}'
    )
    servers = main.load_servers(config_path)
    assert servers == (
        ServerSshConfig(
            name="server1", host="10.0.0.1", port=22, user="u", key="~/.ssh/id_rsa"
        ),
    )


def test_load_servers_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "GPU_MONITOR_SERVERS",
        '{"server2": {"host": "10.0.0.2", "port": 22, '
        '"user": "u", "key": "/keys/id_rsa"}}',
    )
    servers = main.load_servers()
    assert servers == (
        ServerSshConfig(
            name="server2", host="10.0.0.2", port=22, user="u", key="/keys/id_rsa"
        ),
    )


@pytest.mark.anyio
async def test_collect_one_success(monkeypatch: pytest.MonkeyPatch) -> None:
    stats = ServerStats(
        cpu=5.0,
        mem=10.0,
        gpus=[
            GpuInfo(
                index=0,
                model="NVIDIA L20",
                util=45,
                mem_used=1024,
                mem_total=8192,
                mem_percent=12.5,
                temp=62,
                processes=[GpuProcessInfo(user="testuser", name="python", mem_mb=1000)],
            )
        ],
        disks=[],
    )

    def fake_collect(_config: ServerSshConfig, _script: str) -> ServerStats:
        return stats

    monkeypatch.setattr(main, "_collect_via_ssh", fake_collect)

    result = await main.collect_one(
        ServerSshConfig(name="s1", host="10.0.0.1", user="u", key="~/.ssh/id_rsa")
    )
    assert result.error is None
    assert result.stats == stats


@pytest.mark.anyio
async def test_collect_one_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_collect(_config: ServerSshConfig, _script: str) -> ServerStats:
        raise OSError("connection refused")

    monkeypatch.setattr(main, "_collect_via_ssh", fake_collect)

    result = await main.collect_one(
        ServerSshConfig(name="s1", host="10.0.0.1", user="u", key="~/.ssh/id_rsa")
    )
    assert result.error is not None
    assert result.stats is None


@pytest.mark.anyio
async def test_collect_all(monkeypatch: pytest.MonkeyPatch) -> None:
    stats = ServerStats(cpu=5.0, mem=10.0, gpus=[], disks=[])

    def fake_collect(_config: ServerSshConfig, _script: str) -> ServerStats:
        return stats

    monkeypatch.setattr(main, "_collect_via_ssh", fake_collect)

    servers = (
        ServerSshConfig(name="s1", host="10.0.0.2", user="u", key="~/.ssh/id_rsa"),
        ServerSshConfig(name="s2", host="10.0.0.3", user="u", key="~/.ssh/id_rsa"),
    )
    results = await main.collect_all(servers)
    assert len(results) == 2
    assert all(r.stats == stats for r in results)