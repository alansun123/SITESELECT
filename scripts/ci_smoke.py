#!/usr/bin/env python3
"""Cross-platform CI smoke test for SITESELECT CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    cli_path = repo_root / "src" / "siteselect" / "cli.py"
    input_csv = repo_root / "examples" / "candidates.example.csv"
    weights_json = repo_root / "examples" / "weights.example.json"
    out_html = repo_root / "output" / "report_ci.html"

    out_html.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(cli_path),
        "analyze",
        "--input",
        str(input_csv),
        "--weights",
        str(weights_json),
        "--top",
        "3",
        "--out",
        str(out_html),
    ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=repo_root, check=True)

    if not out_html.exists():
        print(f"ERROR: report not found: {out_html}", file=sys.stderr)
        return 1

    if out_html.stat().st_size == 0:
        print(f"ERROR: report is empty: {out_html}", file=sys.stderr)
        return 1

    print(f"Smoke test passed: {out_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
