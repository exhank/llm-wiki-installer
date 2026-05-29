from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import Iterable, Optional

from .command_runner import command_output, run
from .errors import InstallerError
from .terminal_ui import select_options

DEPENDENCY_TOOL_OPTIONS = (
    ("qmd", "qmd (@tobilu/qmd)", "Markdown retrieval and collection indexing"),
    ("rg", "ripgrep (rg)", "Fast full-text search across the vault"),
    ("fzf", "fzf", "Interactive fuzzy file and result selection"),
)


@dataclass(frozen=True)
class ToolVersions:
    node: str
    npm: str
    qmd: str
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

    if "qmd" in selected:
        require_node_22()
        require_executable("npm", "npm is required.")
        run(
            ["npm", "--version"],
            capture=True,
            quiet=True,
            error="npm exists but npm --version failed.",
        )
        if shutil.which("qmd") is None:
            if not install_missing:
                raise InstallerError(
                    "qmd is selected but was not found. Install qmd first, "
                    "or re-run with --tools excluding qmd."
                )
            run(
                ["npm", "install", "-g", "@tobilu/qmd"],
                quiet=quiet,
                error=(
                    "failed to install @tobilu/qmd with npm. Install qmd "
                    "manually, or re-run with --tools excluding qmd."
                ),
            )
        run(
            ["qmd", "--version"],
            capture=True,
            quiet=True,
            error="qmd exists but qmd --version failed.",
        )

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
    qmd_selected = "qmd" in selected
    return ToolVersions(
        node=(
            command_output(["node", "--version"], fallback="unavailable")
            if qmd_selected
            else "skipped"
        ),
        npm=(
            command_output(["npm", "--version"], fallback="unavailable")
            if qmd_selected
            else "skipped"
        ),
        qmd=tool_version("qmd") if qmd_selected else "skipped",
        rg=tool_version("rg") if "rg" in selected else "skipped",
        fzf=tool_version("fzf") if "fzf" in selected else "skipped",
    )


def require_executable(name: str, message: str) -> None:
    if shutil.which(name) is None:
        raise InstallerError(message)


def require_node_22() -> None:
    require_executable("node", "Node.js 22+ is required.")

    version = command_output(["node", "--version"], fallback="")
    major = node_major_version(version)
    if major is None:
        raise InstallerError(
            f"Node.js 22+ is required. Found: {version or 'unavailable'}."
        )
    if major < 22:
        raise InstallerError(f"Node.js 22+ is required. Found: {version}.")


def node_major_version(version: str) -> Optional[int]:
    normalized = version.strip().lstrip("v")
    major = normalized.split(".", 1)[0]
    if not major.isdigit():
        return None
    return int(major)


def tool_version(tool: str) -> str:
    output = command_output([tool, "--version"], fallback="")
    lines = output.splitlines()
    return lines[0] if lines else ""
