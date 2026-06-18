from pathlib import Path

import pytest

from claude_monitor.status import parse_status, read_status, write_status


def test_parse_status_accepts_known_values():
    assert parse_status("idle") == "idle"
    assert parse_status("waiting") == "waiting"


def test_parse_status_falls_back_to_idle_for_monitor_reads():
    assert parse_status("") == "idle"
    assert parse_status("bad") == "idle"


def test_write_status_rejects_unknown_values(tmp_path: Path):
    target = tmp_path / "status.txt"
    with pytest.raises(ValueError):
        write_status(target, "bad")
    assert not target.exists()


def test_write_status_creates_parent_and_replaces_file(tmp_path: Path):
    target = tmp_path / "nested" / "status.txt"
    write_status(target, "idle")
    assert target.read_text(encoding="utf-8") == "idle"
    write_status(target, "waiting")
    assert target.read_text(encoding="utf-8") == "waiting"


def test_write_status_does_not_use_fixed_temp_path(tmp_path: Path):
    target = tmp_path / "status.txt"
    fixed_temp = tmp_path / "status.txt.tmp"
    fixed_temp.write_text("sentinel", encoding="utf-8")

    write_status(target, "waiting")

    assert target.read_text(encoding="utf-8") == "waiting"
    assert fixed_temp.read_text(encoding="utf-8") == "sentinel"


def test_read_status_missing_file_is_idle(tmp_path: Path):
    assert read_status(tmp_path / "missing.txt") == "idle"
