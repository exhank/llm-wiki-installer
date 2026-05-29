from __future__ import annotations

import re
from pathlib import Path

from .command_runner import run


def initialize_qmd(target: Path, quiet: bool = False) -> None:
    result = run(
        ["qmd", "collection", "show", "knowledge-vault"],
        cwd=target,
        capture=True,
        check=False,
    )
    current_path = parse_qmd_collection_path(result.stdout)

    if current_path == str(target):
        if not quiet:
            print("qmd collection knowledge-vault already points to target")
    elif current_path:
        if not quiet:
            print(
                "qmd collection knowledge-vault points to "
                f"{current_path}; rebinding to {target}"
            )
        run(["qmd", "collection", "remove", "knowledge-vault"], cwd=target, quiet=quiet)
        run(
            ["qmd", "collection", "add", str(target), "--name", "knowledge-vault"],
            cwd=target,
            quiet=quiet,
        )
    else:
        run(
            ["qmd", "collection", "add", str(target), "--name", "knowledge-vault"],
            cwd=target,
            quiet=quiet,
        )

    run(["qmd", "update"], cwd=target, quiet=quiet)
    run(["qmd", "embed"], cwd=target, quiet=quiet)


def parse_qmd_collection_path(output: str) -> str:
    for line in output.splitlines():
        match = re.match(r"\s*Path:\s*(.+)$", line)
        if match:
            return match.group(1).strip()
    return ""
