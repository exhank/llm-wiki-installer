from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from .errors import InstallerError


def command_output(command: list[str], fallback: str = "") -> str:
    result = run(command, capture=True, check=False, quiet=True)
    if result.returncode != 0:
        return fallback
    return result.stdout.strip() or fallback


def run(
    command: list[str],
    cwd: Optional[Path] = None,
    capture: bool = False,
    check: bool = True,
    quiet: bool = False,
    error: Optional[str] = None,
) -> subprocess.CompletedProcess[str]:
    stdout = subprocess.PIPE if capture else (subprocess.DEVNULL if quiet else None)
    stderr = subprocess.PIPE if capture else None

    try:
        result = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            check=False,
            text=True,
            stdout=stdout,
            stderr=stderr,
        )
    except FileNotFoundError:
        raise InstallerError(error or f"{command[0]} is required.") from None

    if check and result.returncode != 0:
        raise InstallerError(error or f"command failed: {' '.join(command)}")

    return result
