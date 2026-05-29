from __future__ import annotations

from pathlib import Path

from .errors import InstallerError


def reject_path_symlink(path: Path, root: Path) -> None:
    """Reject writes that would traverse an existing symlink under root."""
    relative = path.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise InstallerError(f"refusing to write through symlink: {current}")
