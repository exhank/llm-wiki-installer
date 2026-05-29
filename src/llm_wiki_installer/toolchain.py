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


def check_required_tools(
    selected_tools: Iterable[str], install_missing: bool = True, quiet: bool = False
) -> None:
    selected = set(selected_tools)
    require_executable("git", "git is required.")

    del install_missing, quiet

    if "rg" in selected:
        require_executable(
            "rg", "rg is required. Recommended install: brew install ripgrep."
        )

    if "fzf" in selected:
        require_executable(
            "fzf", "fzf is required. Recommended install: brew install fzf."
        )


def require_executable(name: str, message: str) -> None:
    if shutil.which(name) is None:
        raise InstallerError(message)
