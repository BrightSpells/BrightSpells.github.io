#!/usr/bin/env python3
"""Generate Hugo data containing the latest commit for each content file."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUTPUT = ROOT / "data" / "gitdates.json"


def git_dates(path: Path) -> list[str]:
    relative = path.relative_to(ROOT)
    result = subprocess.run(
        [
            "git",
            "log",
            "--follow",
            "--format=%aI",
            "--",
            relative.as_posix(),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> None:
    dates: dict[str, dict[str, object]] = {}
    for path in sorted(CONTENT.rglob("*.md")):
        history = git_dates(path)
        if not history:
            continue
        dates[path.relative_to(CONTENT).as_posix()] = {
            "updated": history[0],
            "commitCount": len(history),
        }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(dates, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
