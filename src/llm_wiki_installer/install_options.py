from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .errors import InstallerError

TOOL_CHOICES = ("rg", "fzf")
SKILL_CHOICES = ("Ar9av", "kepano")

USAGE = """Usage: bash install.sh [options] [path/to/knowledge-vault]

Generate an llm-wiki knowledge vault in the target repository root.
When no target path is provided, the current working directory is used.

Options:
  --force  Overwrite generated files in the target vault.
  --no-interactive
           Use the default selection for dependency tools and upstream skills.
  --yes
           Alias for --no-interactive.
  --tools LIST
           Select dependency tools: rg,fzf, all, or none.
  --skills LIST
           Select upstream Skill sources: Ar9av,kepano, all, or none.
  --no-install-tools
           Do not install missing selectable tools.
  --offline
           Do not perform network bootstrap operations.
  --dry-run
           Print the install plan without writing files or running network steps.
  --json
           Print dry-run or final install summaries as JSON.
  -h, --help
           Show this help.

The script refuses to generate into a checked-out llm-wiki generator
repository. When streamed through stdin, the current working directory is used
unless it looks like the generator repository."""


@dataclass(frozen=True)
class Options:  # pylint: disable=too-many-instance-attributes
    force: bool
    target_input: Optional[str]
    interactive: bool = True
    tools: Optional[tuple[str, ...]] = None
    skills: Optional[tuple[str, ...]] = None
    install_tools: bool = True
    offline: bool = False
    dry_run: bool = False
    json_output: bool = False
    show_help: bool = False
    usage: str = USAGE


def parse_options(argv: Iterable[str]) -> Options:  # pylint: disable=too-many-branches
    force = False
    interactive = True
    target_input: Optional[str] = None
    tools: Optional[tuple[str, ...]] = None
    skills: Optional[tuple[str, ...]] = None
    install_tools = True
    offline = False
    dry_run = False
    json_output = False
    args = list(argv)
    index = 0

    while index < len(args):
        arg = args[index]
        if arg == "--force":
            force = True
        elif arg == "--no-interactive":
            interactive = False
        elif arg == "--yes":
            interactive = False
        elif arg == "--tools":
            index += 1
            if index >= len(args):
                raise InstallerError("--tools requires a comma-separated value.")
            tools = parse_selection(args[index], TOOL_CHOICES, "--tools")
        elif arg.startswith("--tools="):
            tools = parse_selection(arg.split("=", 1)[1], TOOL_CHOICES, "--tools")
        elif arg == "--skills":
            index += 1
            if index >= len(args):
                raise InstallerError("--skills requires a comma-separated value.")
            skills = parse_selection(args[index], SKILL_CHOICES, "--skills")
        elif arg.startswith("--skills="):
            skills = parse_selection(arg.split("=", 1)[1], SKILL_CHOICES, "--skills")
        elif arg == "--no-install-tools":
            install_tools = False
        elif arg == "--offline":
            offline = True
            install_tools = False
        elif arg == "--dry-run":
            dry_run = True
        elif arg == "--json":
            json_output = True
        elif arg in ("-h", "--help"):
            return Options(
                force=force,
                target_input=target_input,
                interactive=interactive,
                tools=tools,
                skills=skills,
                install_tools=install_tools,
                offline=offline,
                dry_run=dry_run,
                json_output=json_output,
                show_help=True,
            )
        elif arg.startswith("-"):
            raise InstallerError(f"unknown argument: {arg}")
        elif target_input is None:
            target_input = arg
        else:
            raise InstallerError("only one target path is allowed.")
        index += 1

    return Options(
        force=force,
        target_input=target_input,
        interactive=interactive,
        tools=tools,
        skills=skills,
        install_tools=install_tools,
        offline=offline,
        dry_run=dry_run,
        json_output=json_output,
    )


def parse_selection(
    value: str, allowed_values: tuple[str, ...], option_name: str
) -> tuple[str, ...]:
    normalized = value.strip()
    if normalized == "":
        raise InstallerError(f"{option_name} requires a non-empty value.")
    if normalized == "all":
        return allowed_values
    if normalized == "none":
        return ()

    selected = tuple(
        dict.fromkeys(part.strip() for part in normalized.split(",") if part.strip())
    )
    unknown = sorted(set(selected).difference(allowed_values))
    if unknown:
        allowed = ", ".join((*allowed_values, "all", "none"))
        raise InstallerError(
            f"{option_name} contains unknown value(s): {', '.join(unknown)}. "
            f"Allowed values: {allowed}."
        )
    return selected
