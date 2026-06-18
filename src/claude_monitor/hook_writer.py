from __future__ import annotations

import argparse
from pathlib import Path

from claude_monitor.paths import default_status_path
from claude_monitor.status import write_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write Claude monitor status.")
    parser.add_argument("status", choices=["idle", "waiting"])
    parser.add_argument("--status-file", type=Path, default=default_status_path())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    write_status(args.status_file, args.status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
