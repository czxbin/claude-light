from __future__ import annotations

import os
from pathlib import Path


APP_DIR_NAME = "ClaudeLight"
STATUS_FILE_NAME = "status.txt"


def default_status_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_DIR_NAME / STATUS_FILE_NAME
    return Path.home() / "AppData" / "Local" / APP_DIR_NAME / STATUS_FILE_NAME
