from __future__ import annotations

import shutil
from typing import Iterable

from .errors import InstallerError
from .terminal_ui import select_options

DEPENDENCY_TOOL_OPTIONS = (
    ("rg", "ripgrep (rg)", "Fast full-text search across the vault"),
    ("fzf", "fzf", "Interactive fuzzy file and result selection"),
)


def select_dependency_tools(interactive: bool) -> tuple[str, ...]:
    return select_options(
        "Select dependency tools to enable",
        DEPENDENCY_TOOL_OPTIONS,
        interactive=interactive,
    )


def check_required_tools(selected_tools: Iterable[str]) -> None:
    selected = set(selected_tools)
    require_executable("git", "git is required.")

    if "rg" in selected:
        require_executable(
            "rg",
            "rg is required but not installed. Install it (for example: "
            "brew install ripgrep) or re-run with --tools excluding rg.",
        )

    if "fzf" in selected:
        require_executable(
            "fzf",
            "fzf is required but not installed. Install it (for example: "
            "brew install fzf) or re-run with --tools excluding fzf.",
        )


def require_executable(name: str, message: str) -> None:
    if shutil.which(name) is None:
        raise InstallerError(message)
