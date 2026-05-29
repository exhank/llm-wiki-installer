from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import Iterable

from .command_runner import command_output
from .errors import InstallerError
from .terminal_ui import select_options

DEPENDENCY_TOOL_OPTIONS = (
    ("rg", "ripgrep (rg)", "Fast full-text search across the vault"),
    ("fzf", "fzf", "Interactive fuzzy file and result selection"),
)


@dataclass(frozen=True)
class ToolVersions:
    rg: str
    fzf: str


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


def tool_versions(selected_tools: Iterable[str]) -> ToolVersions:
    selected = set(selected_tools)
    return ToolVersions(
        rg=tool_version("rg") if "rg" in selected else "skipped",
        fzf=tool_version("fzf") if "fzf" in selected else "skipped",
    )


def require_executable(name: str, message: str) -> None:
    if shutil.which(name) is None:
        raise InstallerError(message)


def tool_version(tool: str) -> str:
    output = command_output([tool, "--version"], fallback="")
    lines = output.splitlines()
    return lines[0] if lines else ""
