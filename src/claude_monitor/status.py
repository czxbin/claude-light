from __future__ import annotations

import os
import tempfile
from pathlib import Path


VALID_STATUSES = {"idle", "waiting"}
DEFAULT_STATUS = "idle"


def parse_status(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    if normalized in VALID_STATUSES:
        return normalized
    return DEFAULT_STATUS


def validate_status(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized not in VALID_STATUSES:
        raise ValueError(f"unsupported status: {value!r}")
    return normalized


def read_status(path: Path) -> str:
    try:
        return parse_status(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return DEFAULT_STATUS


def write_status(path: Path, status: str) -> None:
    normalized = validate_status(status)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        fd, temp_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            text=True,
        )
        temp_path = Path(temp_name)
        with os.fdopen(fd, "w", encoding="utf-8") as temp_file:
            temp_file.write(normalized)
        os.replace(temp_path, path)
        temp_path = None
    except Exception:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise
