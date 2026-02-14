#!/usr/bin/env python3
"""Launch SITESELECT Streamlit GUI as a desktop app entrypoint."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _app_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[1]


def main() -> None:
    root = _app_root()
    script = root / "app" / "gui_app.py"

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    os.environ.setdefault("BROWSER_GATHER_USAGE_STATS", "false")

    from streamlit.web.bootstrap import run

    run(
        str(script),
        "",
        [],
        flag_options={
            "server.headless": False,
            "browser.gatherUsageStats": False,
            "server.port": 8501,
        },
    )


if __name__ == "__main__":
    main()
