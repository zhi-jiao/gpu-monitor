from __future__ import annotations

import subprocess
from unittest.mock import Mock

import pytest
from agent import collector


def test_bytes_to_human() -> None:
    assert collector.bytes_to_human(512) == "512.0B"
    assert collector.bytes_to_human(1024) == "1.0K"
    assert collector.bytes_to_human(1024 * 1024) == "1.0M"
    assert collector.bytes_to_human(1024 ** 5) == "1.0P"


def test_parse_gpu_line() -> None:
    gpu = collector._parse_gpu_line("0, NVIDIA L20, 45, 1024, 8192, 62")
    assert gpu["index"] == 0
    assert gpu["model"] == "NVIDIA L20"
    assert gpu["util"] == 45
    assert gpu["mem_used"] == 1024
    assert gpu["mem_total"] == 8192
    assert gpu["mem_percent"] == 12.5
    assert gpu["temp"] == 62
    assert gpu["processes"] == []


def test_parse_gpu_line_bad_format() -> None:
    with pytest.raises(ValueError, match="unexpected nvidia-smi line"):
        collector._parse_gpu_line("45, 1024, 8192")


def test_get_gpus_missing_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "check_output",
        Mock(side_effect=FileNotFoundError("nvidia-smi")),
    )
    assert collector.get_gpus() == []


def test_get_gpus_called_process_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "check_output",
        Mock(side_effect=subprocess.CalledProcessError(1, "nvidia-smi")),
    )
    assert collector.get_gpus() == []


def test_resolve_user_unknown() -> None:
    assert collector._resolve_user(99999999) == "unknown"


def test_collect(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(collector, "get_gpus", list)
    monkeypatch.setattr(collector, "get_gpu_processes", list)
    monkeypatch.setattr(collector, "get_disks", list)
    monkeypatch.setattr(collector.psutil, "cpu_percent", Mock(return_value=12.5))
    mock_mem = Mock()
    mock_mem.percent = 34.0
    monkeypatch.setattr(collector.psutil, "virtual_memory", Mock(return_value=mock_mem))

    assert collector.collect() == {"cpu": 12.5, "mem": 34.0, "gpus": [], "disks": []}